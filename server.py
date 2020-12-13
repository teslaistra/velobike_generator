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
print(stations)
app = FastAPI(title="Hack")


def get_state():
    pass


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ajax/parkings/")
def parking():
    global stations
    for station in stations['Items']:
        if station["AvailableOrdinaryBikes"] <= station["TotalOrdinaryPlaces"]:
            station["AvailableOrdinaryBikes"] = station["AvailableOrdinaryBikes"] + int(
                numpy.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3]))
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
