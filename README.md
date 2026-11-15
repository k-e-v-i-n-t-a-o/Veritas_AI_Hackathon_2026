# Project name
**Track: CLIMATE!!**
**Team: Kevin Tao. :)**
## The problem
Who has this problem, and why does it matter? (2-3 sentences)
Anyone who lives in a city has this problem. It matters because the people in those cities are in high danger of lung or air related diseases, and don't know if the air around them is good, or if it is bad.
## What we built
What goes in, what comes out, and how someone would use it.
like data.     prediction.        i dunno, an application i make?
## How it works
Data: which dataset, how many examples, how we cleaned it.
Model: what we used and why.
## Results
Our baseline scored X. Our model scored Y on held-out test data.
Where it fails, and why we think so.
## What we(i)'d do next
One or two concrete next steps with more time.
## Sources
Datasets, pretrained models, tutorials and AI tools used, with links.



## Run the prediction app

Install the app dependencies and launch the Gradio interface:

```bash
python -m pip install -r requirements.txt
python app.py
```

Enter latitude and longitude to fetch the latest three completed local days and predict the following day's average PM2.5 concentration. The model uses each day's PM2.5 average, weekday, precipitation hours, and maximum 10 m wind speed, scaled with the saved `MyScalerForMyVeryOwnModelYayHappyFace` artifact.

Weather data comes from the Open-Meteo Forecast API. For air-quality observations, set `OPENAQ_API_KEY` in the environment before launching; the app searches for a nearby OpenAQ PM2.5 sensor and uses it when readings cover all three days. Without a key, or if nearby readings are incomplete, it uses the Open-Meteo Air Quality API instead. Open-Meteo PM2.5 is model-derived rather than a station observation.

This hackathon model returns a research estimate, not health guidance.

API references: [Open-Meteo Forecast API](https://open-meteo.com/en/docs), [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), [OpenAQ API](https://docs.openaq.org/).