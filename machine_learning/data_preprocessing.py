#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import os
import json
from data_gathering.common_functions import time_difference


def load_data():
    i = 1

    input_flights = []

    while os.path.isfile("json/flights{}.json".format(i)):
        try:
            with open("json/flights{}.json".format(i), "r") as file:
                data = json.load(file)
                for el in data:
                    flight = [el["arrival_traffic"], el["wind_direction_arrival"], el["wind_speed_arrival"],
                              el["temperature_arrival"], el["dew_point_arrival"], el["pressure_arrival"],
                              el["visibility_arrival"], el["delay_departure"], el["traffic_departure"],
                              el["wind_direction_departure"], el["wind_speed_departure"], el["temperature_departure"],
                              el["dew_point_departure"] / 40, el["pressure_departure"], el["visibility_departure"], el["distance"],
                              el["to latitude"], el["to longitude"],
                              el["from latitude"], el["from longitude"]]

                    for run in range(0,18):
                        flight.append(int(el["to runway {}".format(run)]))
                    for run in range(0,18):
                        flight.append(int(el["from runway {}".format(run)]))

                    time_diff = el["landing_time_difference"]

                    planned_arrival = el["planned_arrival"]
                    landing_time = el["landing_time"]
                    diff = time_difference(planned_arrival, landing_time)
                    input_flights.append((flight, time_diff, diff))
        except:
            print("Couldn't open flights{}.json".format(i))

        i += 1

    return input_flights


def preprocess_for_cnn(data: list, original_landing_diff: bool = True, use_coordinates: bool = True):

    if use_coordinates:
        input_length = len(data[0][0])
    else:
        input_length = len(data[0][0]) - 4

    if original_landing_diff:
        output_length = 10
    else:
        output_length = 3

    np.random.shuffle(data)
    np.random.shuffle(data)
    np.random.shuffle(data)

    x_train = []
    y_train = []
    x_test = []
    y_test = []

    for id, el in enumerate(data):
        fl = el[0]

        flight = [fl[0] / 200, fl[1] / 360, fl[2] / 50,
                  fl[3] / 50, fl[4] / 40, fl[5] / 1045,
                  fl[6] / 9999, fl[7] / 9, fl[8] / 200,
                  fl[9] / 360, fl[10] / 50, fl[11] / 50,
                  fl[12] / 40, fl[13] / 1045, fl[14] / 9999,
                  fl[15] / 16000]

        if use_coordinates:
            flight.append((fl[16] + 90) / 180)
            flight.append((fl[17] + 180) / 360)
            flight.append((fl[18] + 90) / 180)
            flight.append((fl[19] + 180) / 360)

        for runway in fl[-36:]:
            flight.append(runway / 36)

        if not original_landing_diff:
            diff = el[2]
            if diff < -15:
                time_diff = 0
            elif -15 <= diff <= 15:
                time_diff = 1
            else:
                time_diff = 2
        else:
            time_diff = el[1]

        if id <= 0.8 * len(data):
            x_train.append(np.array(flight).reshape((7, 8, 1)))
            y_train.append(time_diff)
        else:
            x_test.append(np.array(flight).reshape((7, 8, 1)))
            y_test.append(time_diff)

    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    return x_train, y_train, x_test, y_test, input_length, output_length
