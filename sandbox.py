#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine_learning import data_preprocessing as dp, models
from data_gathering import data_controler as dc
import numpy as np

# Start gathering data from internet.
#dc.data_controler("/Applications/chromedriver", "Wednesday, Oct 14", "flights2.json")


data = dp.load_data()
x_train, y_train, x_test, y_test, input_shape, output_length = \
    dp.preprocess_for_cnn_or_feed_forward(data, "cnn", original_landing_diff=False)

print(y_train[0])
print(y_test[0])
print(input_shape)

model = models.cnn(input_shape, output_length)

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

model.fit(x_train, y_train, epochs=200, batch_size=30, validation_data=(x_test, y_test))