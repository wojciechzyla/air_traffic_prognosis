#!/usr/bin/python
# -*- coding: utf-8 -*-
from tensorflow import keras

def feed_forward(input_length:int, output_length:int):
    model = keras.models.Sequential()