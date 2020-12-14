from fastapi import FastAPI
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime as dt
import requests
import warnings
import json
import numpy

warnings.simplefilter('ignore', InsecureRequestWarning)

record = requests.get('https://velobike.ru/ajax/parkings/', verify=False).text
stations = json.loads(record)

for station in stations['Items']:
    station["IsLocked"] = False
    station["AvailableOrdinaryBikes"] = int(station["FreeOrdinaryPlaces"] / 2)
    station["FreeOrdinaryPlaces"] = int(station["FreeOrdinaryPlaces"] - station["AvailableOrdinaryBikes"])

app = FastAPI(title="Velobike")

night = {"actions": [-1, 0, 1], "p": [0.1, 0.8, 0.1]}
morning = {"actions": [-1, 0, 1], "p": [0.2, 0.6, 0.2]}
day_peak = {"actions": [-2, -1, 0, 1, 2], "p": [0.2, 0.2, 0.2, 0.2, 0.2]}
evening = {"actions": [-2, -1, 0, 1, 2], "p": [0.1, 0.3, 0.2, 0.3, 0.1]}


def get_state():
    time_now = dt.datetime.now()
    hour = time_now.hour

    if 0 <= hour <= 7:
        return night
    elif 12 >= hour >= 8:
        return morning
    elif 13 <= hour <= 17:
        return day_peak
    elif 18 <= hour <= 23:
        return evening


@app.get("/")
async def root():
    print(get_state())
    return {"message": "Hello World"}


@app.get("/ajax/parkings/")
def parking():
    global stations
    for station in stations['Items']:
        if station["AvailableOrdinaryBikes"] <= station["TotalOrdinaryPlaces"]:
            actions, p = get_state()
            station["AvailableOrdinaryBikes"] = station["AvailableOrdinaryBikes"] + int(
                numpy.random.choice(actions, p))
        if station["AvailableOrdinaryBikes"] < 0:
            station["AvailableOrdinaryBikes"] = 0
        elif station["AvailableOrdinaryBikes"] > station["TotalOrdinaryPlaces"]:
            station["AvailableOrdinaryBikes"] = station["TotalOrdinaryPlaces"]
        station["FreePlaces"] = int(station["TotalOrdinaryPlaces"] - station["AvailableOrdinaryBikes"])
        station["FreeOrdinaryPlaces"] = int(station["TotalOrdinaryPlaces"] - station["AvailableOrdinaryBikes"])
    return stations


@app.get("/reset")
async def reset():
    global stations
    warnings.simplefilter('ignore', InsecureRequestWarning)

    record = requests.get('https://velobike.ru/ajax/parkings/', verify=False).text
    stations = json.loads(record)

    for station in stations['Items']:
        station["IsLocked"] = False
        station["AvailableOrdinaryBikes"] = int(station["FreeOrdinaryPlaces"] / 2)
        station["FreeOrdinaryPlaces"] = int(station["FreeOrdinaryPlaces"] - station["AvailableOrdinaryBikes"])
    return stations
