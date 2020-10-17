#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import os
import json
from data_gathering.common_functions import time_difference

class UnknownModelType(Exception):
    def __init__(self, func, models):
        if func and models:
            msg = "{} called with different model_type than {}".format(func, models)
        else:
            msg = "Preprocessing function called with wrong model_type"
        super().__init__(msg)


# Load data from from all flights_<number>.json files.
# Function return list of tuples. Each tuple contains flight info,
# information about delay calculted while gathering data, and time difference between
# planned landing and actual landing.
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
                              el["dew_point_departure"], el["pressure_departure"], el["visibility_departure"], el["distance"],
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


# Function makes data suitable for cnn or feed_forward model depending on network_type variable.
# User can specify what type of labels should be used by providing original_landing_diff.
# By default it is set to True, so there are 10 possible outputs corresponding to different delay ranges
# (check time_difference_range function from data_gathering.common_functions.py).
# If original_landing_diff is set to False then there are only 3 outputs (early, +/- 15 min to planned arrival, late).
# Function return training and test data, input dimension and output length.
def preprocess_for_cnn_or_feed_forward(data: list, network_type: str, original_landing_diff: bool = True):

    if network_type == "feed_forward":
        input_shape = len(data[0][0])
    elif network_type == "cnn":
        input_shape = (7, 8, 1)
    else:
        raise UnknownModelType("preprocess_for_cnn_or_feed_forward", "cnn or feed_forward")

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

        flight = [fl[0] / 200, fl[1] / 360, fl[2] / 50, fl[3] / 50, fl[4] / 40, fl[5] / 1045, fl[6] / 9999, fl[7] / 9,
                  fl[8] / 200, fl[9] / 360, fl[10] / 50, fl[11] / 50, fl[12] / 40, fl[13] / 1045, fl[14] / 9999,
                  fl[15] / 16000, (fl[16] + 90) / 180, (fl[17] + 180) / 360, (fl[18] + 90) / 180, (fl[19] + 180) / 360]

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
            if network_type == "cnn":
                x_train.append(np.array(flight).reshape(input_shape))
            else:
                x_train.append(np.array(flight))
            y_train.append(time_diff)
        else:
            if network_type == "cnn":
                x_test.append(np.array(flight).reshape(input_shape))
            else:
                x_test.append(np.array(flight))
            y_test.append(time_diff)

    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    return x_train, y_train, x_test, y_test, input_shape, output_length
