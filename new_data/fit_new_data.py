import csv

VALUE_INDEX = 0
DATE_INDEX = 1
DAY_UNITS_DIGIT_INDEX = 9
WEATHER_FILE = "austin_w.csv"
AIR_QUALITY_FILE = "austin_a.csv"

new = []
d = []
weekday = 5
last_day = "0"
rn = 0
with open(WEATHER_FILE, mode='r') as file:
    weather = csv.reader(file)
    next(weather)
    weather = list(weather)
with open(AIR_QUALITY_FILE, mode='r') as file:
    data = csv.reader(file)
    header = next(data)
    for row in data:
        date = row[DATE_INDEX][DAY_UNITS_DIGIT_INDEX]
        
        if date != last_day:
            if rn == len(weather):
                print(f"Stopped at {rn}")
                break
            new.append([f"{sum(d)/len(d):.4f}", weekday, weather[rn][1], weather[rn][2], weather[rn][3], weather[rn][4], weather[rn][5]])
            #if int(last_day)+1 != int(date):
            #    if int(date)-1 != 0:
            #        print(row)
            last_day = date
            weekday += 1
            if weekday == 7:
                weekday = 0
            d.clear()
            rn += 1
        
        d.append(float(row[VALUE_INDEX]))

with open("/new_data.csv", mode='w') as file:
    writer = csv.writer(file)
    writer.writerows(new)