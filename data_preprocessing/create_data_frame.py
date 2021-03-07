#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import pandas as pd
import os
from data_gathering.common_functions import time_difference


def load_data():
    """
    Function loads data and changes it to DataFrame

    :return: dataframe
    """

    data_frames = []
    i = 1
    while os.path.isfile("json/flights{}.json".format(i)):
        try:
            with open("json/flights{}.json".format(i), "r") as file:
                data = json.load(file)
                            
                df = pd.DataFrame.from_dict(data)
                data_frames.append(df)

        except:
            print("Couldn't open flights{}.json".format(i))

        i += 1

    df = pd.concat(data_frames, ignore_index=True)
    return df


def preprocess_data(df:pd.DataFrame, target_classes = 'original'):
    """
    Finction changes number of target classes if specified

    :param df: Pandas DataFrame
    :param target_classes: possible values are: 'original','three','two'.
    Parameter specifies if user want's to use original target classes;
    only three representing if plane was early, on time or late;
    two classes representing if plane was on time/early or late.

    :return: Preprocessed DataFrame
    """
    if target_classes != 'original' and target_classes != 'two' and target_classes != 'three':
        raise ValueError("argument target_classes different from {'original','three','two'} ")

    cols_to_drop = []
    for run in range(0, 18):
        cols_to_drop.append("runway {}".format(run))

    cols_t_drop2 = ['planned_arrival', 'flight_number', 'from_airport', 'to_airport', 'aircraft_no', 'landing_time']

    if target_classes != "original":
        for id in df.index:
            planned_arrival = df["planned_arrival"][id]
            landing_time = df["landing_time"][id]
            diff = time_difference(str(planned_arrival), str(landing_time))

            if target_classes == "three":
                if diff < -15:
                    df["landing_time_difference"][id] = 0
                elif -15 <= diff <= 15:
                    df["landing_time_difference"][id] = 1
                else:
                    df["landing_time_difference"][id] = 2
            else:
                if diff <= 15:
                    df["landing_time_difference"][id] = 0
                else:
                    df["landing_time_difference"][id] = 1

    try:
        df = df.drop(columns=cols_to_drop)
    except:
        pass

    df = df.drop(columns=cols_t_drop2)

    return df
