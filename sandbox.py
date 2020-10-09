#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from common_functions import time_difference


def load_data():
    i = 1

    input_flights = []

    while os.path.isfile("json/flights{}.json".format(i)):
        try:
            with open("json/flights{}.json".format(i), "r") as file:
                data = json.load(file)
                for el in data:
                    flight = [el["arrival_traffic"] / 200, el["wind_direction_arrival"] / 360, el["wind_speed_arrival"] / 50,
                              el["temperature_arrival"] / 50,el["dew_point_arrival"] / 40, el["pressure_arrival"] / 1045,
                              el["visibility_arrival"] / 9999, el["delay_departure"] / 9,el["traffic_departure"] / 200,
                              el["wind_direction_departure"] / 360, el["wind_speed_departure"] / 50, el["temperature_departure"] / 50,
                              el["dew_point_departure"] / 40, el["pressure_departure"] / 1045, el["visibility_departure"] / 9999, el["distance"] / 16000]
                    """(el["to latitude"] + 90) / 180, (el["to longitude"] + 180) / 360,
                    (el["from latitude"] + 90) / 180, (el["from longitude"] + 180) / 360,"""
                    for run in range(0,18):
                        flight.append(el["to runway {}".format(run)] / 36)
                    for run in range(0,18):
                        flight.append(el["from runway {}".format(run)] / 36)

                    planned_arrival = el["planned_arrival"]
                    landing_time = el["landing_time"]
                    diff = time_difference(planned_arrival, landing_time)
                    if diff < -15:
                        time_diff = [1, 0, 0]
                    elif -15 <= diff <= 15:
                        time_diff = [0, 1, 0]
                    else:
                        time_diff = [0, 0, 1]
                    input_flights.append((flight, time_diff))
        except:
            print("Couldn't open flights{}.json".format(i))

        i += 1
    return input_flights