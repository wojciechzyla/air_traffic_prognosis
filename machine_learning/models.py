#!/usr/bin/python
# -*- coding: utf-8 -*-
from tensorflow import keras
from typing import Tuple

def feed_forward(input_length:int, output_length:int):
    inp = keras.Input(shape=(input_length,))
    l1 = keras.layers.Dense(65, activation='relu', kernel_regularizer='l1')
    d1 = keras.layers.Dropout(0.5)
    l2 = keras.layers.Dense(60, activation='relu', kernel_regularizer='l1')
    d2 = keras.layers.Dropout(0.5)
    f = keras.layers.Dense(output_length, activation='softmax')

    model = keras.models.Sequential([inp, l1, d1, l2, d2, f])

    return model


def cnn(shape: Tuple[int, int, int], output_length:int):
    cnn1 = keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=shape)
    mp1 = keras.layers.MaxPool2D(pool_size=(2, 2), padding='same')
    drop1 = keras.layers.Dropout(0.25)

    cnn2 = keras.layers.Conv2D(64, (2, 2), padding='same', activation='relu')
    mp2 = keras.layers.MaxPool2D(pool_size=(2, 2))
    drop2 = keras.layers.Dropout(0.25)

    cnn3 = keras.layers.Conv2D(64, (2, 2), padding='same', activation='relu')
    mp3 = keras.layers.MaxPool2D(pool_size=(2, 2))
    drop3 = keras.layers.Dropout(0.25)

    flat = keras.layers.Flatten()
    dense = keras.layers.Dense(70, activation='relu', kernel_regularizer='l1')
    drop4 = keras.layers.Dropout(0.5)
    final = keras.layers.Dense(output_length, activation='softmax')

    model = keras.models.Sequential([cnn1, mp1, drop1, cnn2, mp2, drop2, cnn3, mp3,
                                    drop3, flat, dense, drop4, final])

    return model