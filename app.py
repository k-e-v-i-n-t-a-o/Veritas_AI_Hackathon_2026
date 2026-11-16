"""Gradio app for next-day PM2.5 predictions from the trained model."""

from __future__ import annotations

import html
import json
import math
import os
import pickle
import statistics
import ssl
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import gradio as gr
import certifi
import geonamescache


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "MyVeryOwnModelThatImVeryProudOvAndHelloIfUrReadingThis.pkl"
SCALER_PATH = ROOT / "MyScalerForMyVeryOwnModelYayHappyFace"
OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
OPENAQ_URL = "https://api.openaq.org/v3"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
DEFAULT_LATITUDE = 29.7604
DEFAULT_LONGITUDE = -95.3698


def load_city_catalog() -> tuple[
    list[tuple[str, str]], dict[str, tuple[float, float, str, str, str]]
]:
    geonames = geonamescache.GeonamesCache()
    countries = geonames.get_countries()
    choices: list[tuple[str, str]] = []
    city_data: dict[str, tuple[float, float, str, str, str]] = {}
    for city in geonames.get_cities().values():
        city_id = str(city["geonameid"])
        city_name = str(city["name"])
        country_code = str(city.get("countrycode", ""))
        country_name = countries.get(country_code, {}).get("name", country_code)
        region = str(city.get("admin1code", "")).strip()
        latitude = float(city["latitude"])
        longitude = float(city["longitude"])
        label = (
            f"{city_name}, {region}, {country_name}"
            if region
            else f"{city_name}, {country_name}"
        )
        choices.append((label, city_id))
        city_data[city_id] = (latitude, longitude, label, city_name, country_code)
    choices.sort(key=lambda choice: choice[0].casefold())
    return choices, city_data


CITY_CHOICES, CITY_DATA = load_city_catalog()
DEFAULT_CITY_ID = min(
    (
        city_id
        for city_id, city in CITY_DATA.items()
        if city[3] == "Houston" and city[4] == "US"
    ),
    key=lambda city_id: abs(CITY_DATA[city_id][0] - DEFAULT_LATITUDE)
    + abs(CITY_DATA[city_id][1] - DEFAULT_LONGITUDE),
)


def city_map_html(latitude: float, longitude: float, label: str) -> str:
    padding = 0.12
    bounds = ",".join(
        str(value)
        for value in (
            max(-180, longitude - padding),
            max(-85, latitude - padding),
            min(180, longitude + padding),
            min(85, latitude + padding),
        )
    )
    map_url = (
        "https://www.openstreetmap.org/export/embed.html?"
        + urlencode(
            {"bbox": bounds, "layer": "mapnik", "marker": f"{latitude},{longitude}"}
        )
    )
    safe_label = html.escape(label, quote=True)
    return (
        f'<iframe src="{map_url}" title="Map showing {safe_label}" '
        'loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
        'style="width:100%;height:380px;border:0;border-radius:4px" '
        'allowfullscreen></iframe>'
    )


def select_city(city_id: str) -> tuple[float, float, str]:
    latitude, longitude, label, _, _ = CITY_DATA[city_id]
    return latitude, longitude, city_map_html(latitude, longitude, label)


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[Any, Any]:
    with MODEL_PATH.open("rb") as model_file:
        model = pickle.load(model_file)
    with SCALER_PATH.open("rb") as scaler_file:
        scaler = pickle.load(scaler_file)
    return model, scaler


def request_json(url: str, api_key: str | None = None) -> dict[str, Any]:
    headers = {"User-Agent": "AirAheadHackathon/1.0"}
    if api_key:
        headers["X-API-Key"] = api_key
    request = Request(url, headers=headers)
    with urlopen(request, timeout=20, context=SSL_CONTEXT) as response:
        return json.load(response)


def open_meteo_weather(latitude: float, longitude: float) -> dict[str, Any]:
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "precipitation_hours,wind_speed_10m_max",
            "timezone": "auto",
            "past_days": 4,
            "forecast_days": 1,
        }
    )
    return request_json(f"{OPEN_METEO_WEATHER_URL}?{query}")


def open_meteo_pm25(
    latitude: float, longitude: float, timezone_name: str
) -> dict[str, float]:
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5",
            "timezone": timezone_name,
            "past_days": 4,
            "forecast_days": 1,
        }
    )
    payload = request_json(f"{OPEN_METEO_AIR_URL}?{query}")
    hourly = payload.get("hourly", {})
    timestamps = hourly.get("time", [])
    values = hourly.get("pm2_5", [])
    grouped: dict[str, list[float]] = {}
    for timestamp, value in zip(timestamps, values):
        if value is None:
            continue
        grouped.setdefault(timestamp[:10], []).append(float(value))
    return {day: statistics.mean(samples) for day, samples in grouped.items()}


def _openaq_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    results = payload.get("results", payload.get("result", []))
    return results if isinstance(results, list) else []


def openaq_pm25(
    latitude: float,
    longitude: float,
    days: list[str],
    timezone_name: str,
    api_key: str,
) -> tuple[dict[str, float], str]:
    location_query = urlencode(
        {"coordinates": f"{latitude},{longitude}", "radius": 25000, "limit": 100}
    )
    locations = _openaq_results(
        request_json(f"{OPENAQ_URL}/locations?{location_query}", api_key)
    )
    locations.sort(key=lambda location: location.get("distance", math.inf))

    local_zone = ZoneInfo(timezone_name)
    start = datetime.combine(date.fromisoformat(days[0]), time.min, tzinfo=local_zone)
    end = datetime.combine(
        date.fromisoformat(days[-1]) + timedelta(days=1), time.min, tzinfo=local_zone
    )
    measurements_query = urlencode(
        {
            "datetime_from": start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "datetime_to": end.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "limit": 1000,
        }
    )

    for location in locations[:10]:
        location_id = location.get("id")
        if location_id is None:
            continue
        sensors = _openaq_results(
            request_json(f"{OPENAQ_URL}/locations/{location_id}/sensors", api_key)
        )
        for sensor in sensors:
            parameter = sensor.get("parameter", {})
            parameter_name = str(parameter.get("name", "")).lower().replace(".", "")
            if parameter_name not in {"pm25", "pm2_5"}:
                continue
            sensor_id = sensor.get("id")
            if sensor_id is None:
                continue
            measurements = _openaq_results(
                request_json(
                    f"{OPENAQ_URL}/sensors/{sensor_id}/measurements?{measurements_query}",
                    api_key,
                )
            )
            grouped: dict[str, list[float]] = {}
            for measurement in measurements:
                timestamp = measurement.get("datetime", {})
                timestamp = timestamp.get("utc") if isinstance(timestamp, dict) else timestamp
                if timestamp is None:
                    period = measurement.get("period", {})
                    timestamp = period.get("datetimeFrom", period.get("datetime_from", {}))
                    timestamp = timestamp.get("utc") if isinstance(timestamp, dict) else timestamp
                value = measurement.get("value")
                if timestamp is None or value is None:
                    continue
                measured_at = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
                local_day = measured_at.astimezone(local_zone).date().isoformat()
                if local_day in days:
                    grouped.setdefault(local_day, []).append(float(value))
            if all(grouped.get(day) for day in days):
                means = {day: statistics.mean(grouped[day]) for day in days}
                return means, str(location.get("name", "Nearby OpenAQ station"))

    raise ValueError("No nearby OpenAQ PM2.5 sensor has readings for all three days.")


def completed_days(weather: dict[str, Any]) -> tuple[list[str], str]:
    daily = weather.get("daily", {})
    dates = daily.get("time", [])
    timezone_name = weather.get("timezone", "UTC")
    try:
        local_today = datetime.now(ZoneInfo(timezone_name)).date()
    except Exception:
        timezone_name = "UTC"
        local_today = datetime.now(timezone.utc).date()
    available = [day for day in dates if date.fromisoformat(day) < local_today]
    if len(available) < 3:
        raise ValueError("Weather data did not include three completed days for this location.")
    return available[-3:], timezone_name


def build_features(
    days: list[str],
    pm25_by_day: dict[str, float],
    weather: dict[str, Any],
) -> list[float | int]:
    daily = weather["daily"]
    weather_by_day = {
        day: (rain_hours, max_wind)
        for day, rain_hours, max_wind in zip(
            daily["time"], daily["precipitation_hours"], daily["wind_speed_10m_max"]
        )
    }
    features: list[float | int] = []
    for day in days:
        if day not in pm25_by_day or day not in weather_by_day:
            raise ValueError(f"A required PM2.5 or weather reading is missing for {day}.")
        rain_hours, max_wind = weather_by_day[day]
        if rain_hours is None or max_wind is None:
            raise ValueError(f"A required weather reading is missing for {day}.")
        features.extend(
            [
                float(pm25_by_day[day]),
                date.fromisoformat(day).weekday(),
                float(rain_hours),
                float(max_wind),
            ]
        )
    return features


def air_quality_band(value: float) -> str:
    if value < 0:
        return "Below zero (model output)"
    if value <= 9:
        return "Good"
    if value <= 35.4:
        return "Moderate"
    if value <= 55.4:
        return "Unhealthy for sensitive groups"
    if value <= 125.4:
        return "Unhealthy"
    if value <= 225.4:
        return "Very unhealthy"
    return "Hazardous"


def prediction_vibe(value: float) -> str:
    if value < 0:
        return "The model found negative pollution. Either magic, or a math problem."
    if value <= 5:
        return "Pristine rainforest air. Somewhere, a leaf is doing a great job."
    if value <= 9:
        return "Clean suburban air. The lawns are thriving, and so are your lungs."
    if value < 15:
        return "A little haze in the plot: not rainforest-fresh, not refinery-adjacent."
    if value <= 25:
        return "Average air. Nothing to write home about, unless home is very dramatic."
    if value <= 50:
        return "You might be living next to an oil refinery. That is a joke, not a diagnosis."
    if value <= 150:
        return "Wildfire-smoke vibes. Check local air-quality advisories before heading out."
    return "The model says you should probably evacuate. Check official local guidance; this is not an emergency alert."


def predict_air_quality(
    latitude: float | None, longitude: float | None, air_source: str
) -> tuple[str, list[list[Any]]]:
    if latitude is None or longitude is None:
        return "## Enter both coordinates to run a prediction.", []
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return "## Coordinates are outside the valid latitude/longitude range.", []

    try:
        weather = open_meteo_weather(latitude, longitude)
        days, timezone_name = completed_days(weather)
        if air_source == "OpenAQ monitor readings":
            api_key = os.getenv("OPENAQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAQ monitor data requires an API key. Set OPENAQ_API_KEY "
                    "in the environment where app.py is running, then restart the app. "
                    "Choose Open-Meteo CAMS below only if you want modeled PM2.5 values."
                )
            pm25_by_day, station_name = openaq_pm25(
                latitude, longitude, days, timezone_name, api_key
            )
            source = f"OpenAQ monitor: {station_name}"
        elif air_source == "Open-Meteo CAMS model":
            pm25_by_day = open_meteo_pm25(latitude, longitude, timezone_name)
            source = "Open-Meteo CAMS model"
        else:
            raise ValueError("Choose a supported PM2.5 data source.")

        features = build_features(days, pm25_by_day, weather)
        model, scaler = load_artifacts()
        prediction = float(model.predict(scaler.transform([features]))[0])
        if not math.isfinite(prediction):
            raise ValueError("The model returned a non-finite prediction.")

        rows = []
        for day in days:
            rain_hours, max_wind = next(
                (rain, wind)
                for weather_day, rain, wind in zip(
                    weather["daily"]["time"],
                    weather["daily"]["precipitation_hours"],
                    weather["daily"]["wind_speed_10m_max"],
                )
                if weather_day == day
            )
            rows.append(
                [
                    day,
                    f"{pm25_by_day[day]:.1f}",
                    f"{float(rain_hours):.1f}",
                    f"{float(max_wind):.1f}",
                ]
            )

        result = (
            f"## {prediction:.1f} µg/m³\n"
            f"**Predicted next-day PM2.5 average** · {air_quality_band(prediction)}\n\n"
            f"**Vibe check:** {prediction_vibe(prediction)}\n\n"
            f"PM2.5 source: {source}  \n"
            "Weather source: Open-Meteo  \n"
            "This is a research estimate, not health guidance."
        )
        return result, rows
    except Exception as error:
        return f"## Prediction unavailable\n{error}", []


CSS = """
.gradio-container { max-width: 1080px !important; }
.hero { padding: 2rem 0 1.2rem; border-bottom: 1px solid #d6e2df; }
.hero h1 { color: #123b3b; font-size: 2.5rem; margin-bottom: .3rem; }
.hero p { color: #4a6967; font-size: 1rem; }
.result-panel { background: #e6f4ee; border-left: 4px solid #ec795b; padding: 1rem 1.2rem; }
footer { display: none !important; }
"""

selected_city = CITY_DATA[DEFAULT_CITY_ID]

with gr.Blocks(
    title="Air Ahead | Next-day PM2.5",
) as demo:
    gr.Markdown(
        "# Air Ahead\n### Tomorrow's air, grounded in your location.",
        elem_classes="hero",
    )
    with gr.Row():
        city = gr.Dropdown(
            choices=CITY_CHOICES,
            value=DEFAULT_CITY_ID,
            label="City",
            filterable=True,
        )
    with gr.Row():
        latitude = gr.Number(label="Latitude", value=selected_city[0], precision=6)
        longitude = gr.Number(label="Longitude", value=selected_city[1], precision=6)
        predict_button = gr.Button("Predict tomorrow", variant="primary")
    city_map = gr.HTML(
        value=city_map_html(selected_city[0], selected_city[1], selected_city[2]),
        label="Selected city map",
        min_height=390,
    )
    city.change(
        fn=select_city,
        inputs=city,
        outputs=[latitude, longitude, city_map],
        api_visibility="private",
    )
    air_source = gr.Radio(
        choices=["OpenAQ monitor readings", "Open-Meteo CAMS model"],
        value="OpenAQ monitor readings",
        label="Past PM2.5 data source",
        info="OpenAQ uses nearby station observations. The CAMS option uses modeled estimates.",
    )
    result = gr.Markdown(elem_classes="result-panel")
    history = gr.Dataframe(
        headers=["Local day", "PM2.5 (µg/m³)", "Rain (hours)", "Max wind (km/h)"],
        datatype=["str", "str", "str", "str"],
        interactive=False,
        label="Three-day input window",
    )
    predict_button.click(
        fn=predict_air_quality,
        inputs=[latitude, longitude, air_source],
        outputs=[result, history],
    )


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="orange", neutral_hue="slate"),
        css=CSS,
    )