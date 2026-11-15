import csv

new = []
d = []
weekday = 4
last_day = "26"
rn = 0
with open("open-meteo-29.77N95.44W17m.csv", mode='r') as file:
    weather = csv.reader(file)
    next(weather)
    weather = list(weather)
with open("air_quality_data.csv", mode='r') as file:
    data = csv.reader(file)
    header = next(data)
    for row in data:
        date = row[0][8] + row[0][9]
        
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
        
        d.append(float(row[-1]))

with open("edited_data.csv", mode='w') as file:
    writer = csv.writer(file)
    writer.writerows(new)