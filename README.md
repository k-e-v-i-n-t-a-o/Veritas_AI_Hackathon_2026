# Project name
**Track: CLIMATE!!**

**Team: Kevin Tao. :)**
## The problem
The problem is that anyone who lives in a city is at high risk of lung or air related diseases, and need to know when the air surrounding them is above the advisable line for living in. According to the [Climate & Clean Air Coalition](https://www.ccacoalition.org/news/world-health-organization-releases-new-global-air-pollution-data), ==9 out of 10 people breathe air containing high levels of pollutants==, which poses a massive risk for most of Earth.
## What we built
We built an application that takes a user-inputed coordinate(longitude and latitude) and gives them our model's prediction of tomorrow's air quality(PM2.5 µg/m³). This gives them the general idea of where they want to spend their day to reduce their risk of lung related diseases.
## How it works
Data: which dataset, how many examples, how we cleaned it.

Model: what we used and why.
## Results
Our baseline scored X. Our model scored Y on held-out test data.
Where it fails, and why we think so.
## What we(i)'d do next

 - retrain the model using data from around the world, because right now it is predicting Houston air quality pretty well, but other places... not so good.
 - automate the getting of the data, because it took me an extremely long time to get and filter the data, and if I want to do it around the world, that is not what I want to do.

## Sources
Datasets, pretrained models, tutorials and AI tools used, with links.

 - Data was taken from Open Meteo(open-meteo.com) and OpenAQ(https://explore.openaq.org/#1.2/20/40).
 - Copilot used to create the application(app.py).
 - [scikit-learn site](https://scikit-learn.org/stable/) and Gemini helped me understand and use the sklearn machine learning library, and the actual code in the notebook was done by me!
 - API references: [Open-Meteo Forecast API](https://open-meteo.com/en/docs), [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), [OpenAQ API](https://docs.openaq.org/).

## Run the prediction app(by copilot)

Install the app dependencies and launch the Gradio interface:
When prompted in the terminal, enter your OpenAQ API key

```bash
python -m pip install -r requirements.txt
read -s "OPENAQ_API_KEY?OpenAQ API key: "
export OPENAQ_API_KEY
.venv/bin/python app.py
```

Enter latitude and longitude to fetch the latest three completed local days and predict the following day's average PM2.5 concentration.

Weather data comes from the Open-Meteo Forecast API. For air-quality observations, set `OPENAQ_API_KEY` in the environment before launching; the app searches for a nearby OpenAQ PM2.5 sensor and uses it when readings cover all three days. Without a key, or if nearby readings are incomplete, it uses the Open-Meteo Air Quality API instead. Open-Meteo PM2.5 is model-derived rather than a station observation.

This model returns a research estimate, not health guidance.