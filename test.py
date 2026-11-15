import csv

with open("air_quality_data.csv", mode='r') as file:
    data = csv.reader(file)
    header = next(data)
    print(list(data)[43195][8])