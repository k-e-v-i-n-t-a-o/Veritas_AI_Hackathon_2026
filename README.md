the main file is myVeryOwnModel.ipynb
# Air Ahead
**Track: CLIMATE!!**

**Team: Kevin Tao. :)**
## The problem
Anyone who lives in a city is at high risk of lung or air related diseases, and needs to know when the air surrounding them is above the advisable line for living in. According to the [Climate & Clean Air Coalition](https://www.ccacoalition.org/news/world-health-organization-releases-new-global-air-pollution-data), 9 out of 10 people breathe air containing high levels of pollutants, which poses a massive risk for most of Earth's population.
## What we built
We built an application that takes a user-inputed coordinate(longitude and latitude) and gives them our model's prediction of tomorrow's air quality(PM2.5 µg/m³). This gives them the general idea of where they want to spend their day to reduce their risk of lung related diseases.
## How it works
Data:
 - Air Quality data came from Houston, TX from OpenAQ(openaq.org)
 - Weather data came from Houston, TX from Open Meteo(open-meteo.com)
 - I created a python script to filter and edit the data in a format so that the model could easily gobble it up.
 - The model then ate through all the data.
 - After the model was trained and tested, it got some new data from Austin, TX, and Delhi in India. It didn't completely blow up when we gave it the data, so that was good:).

Model:
 - The model we used was a scikit-learn linear regression model.
    - Regression means it is outputting a number on a spectrumn instead of classes
    - Linear means it draws a linear line through each data parameter and decides something based on the position of the dot vs the line
    - scikit-learn is the library that provies all these nice functional functions!
 - I tried some other regression models scikit-learn provides, such as random forest, but they all performed less good than the linear regression model.

## Results
The baseline scored -100,000 on a scale from negative infinity to 1.0 on data from Austin, where 1.0 is a perfect model. After removing some of the paremeters(WeekDay,Temperature,DaylightTime,RainSum), the score went up all the way to negative one, and then up to 0.5! However, the model is still highly inaccurate, with one of the test points being at 300, and the model predicting 150. This is likely because the model was trained on data from Houston, TX and was trying to predict data all the way in India, causing the massive error margin.
I also had the model multiply the result it got by x1.1, because this is better to have false alarms rather than everyone dying. Even though this lowered the model's overall accuracy, it made the real-fake-real-life implementation better.
## What we'd do next
 - retrain the model using data from around the world, because right now it is predicting Houston air quality pretty well, but other places... not so good.
 - automate the getting of the data, because it took me an extremely long time to get and filter the data, and if I want to do it around the world, that is not what I want to do.
## Sources
 - Data was taken from Open Meteo(https://open-meteo.com) and OpenAQ(https://explore.openaq.org/#1.2/20/40).
 - Copilot was used to create the application(app.py).
 - [scikit-learn site](https://scikit-learn.org/stable/) and Gemini helped me understand and use the sklearn machine learning library, and the actual code in the notebook and the other notebook and the random python files were all done by me!
 - API references: [Open-Meteo Forecast API](https://open-meteo.com/en/docs), [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), [OpenAQ API](https://docs.openaq.org/).
 - Copilot made the name of the project. i think its pretty cool!
 - Map (in the site): [Open Street Map](https://www.openstreetmap.org/#map=5/38.01/-95.84)
## What i have added of my own
 - the suggested project was 4.3.2 Next-day air quality forecast
 - I know houston(where I lived) is pretty dry, so I thought the rain would impact the polution more. But that was one of the datapoints i removed later on because it did nothing and made more data to process
 - The program outputs a unprofessional message based on the predicted air quality, to reflect that this is not a very accurate model and will get many things wrong.
## How to run the prediction app (by Copilot)

Install the app dependencies and launch the Gradio interface:
When prompted in the terminal, enter your OpenAQ API key

```bash
read -s "OPENAQ_API_KEY?OpenAQ API key: "
export OPENAQ_API_KEY
.venv/bin/python app.py
```

Enter latitude and longitude to fetch the latest three completed local days and predict the following day's average PM2.5 concentration.

Weather data comes from the Open-Meteo Forecast API. For air-quality observations, set `OPENAQ_API_KEY` in the environment before launching; the app searches for a nearby OpenAQ PM2.5 sensor and uses it when readings cover all three days. Without a key, or if nearby readings are incomplete, it uses the Open-Meteo Air Quality API instead. Open-Meteo PM2.5 is model-derived rather than a station observation.

This model returns a research estimate, not health guidance.

.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.

### :)