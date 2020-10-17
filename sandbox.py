#!/usr/bin/python
# -*- coding: utf-8 -*-
#from machine_learning import data_preprocessing as dp, models
from data_gathering import data_controler as dc
import numpy as np

# Start gathering data from internet.
dc.data_controler("/Applications/chromedriver", "Wednesday, Oct 14", "flights2.json")


"""data = dp.load_data()
x_train, y_train, x_test, y_test, input_length, output_length = dp.preprocess_for_cnn(data, original_landing_diff=False, use_coordinates=True)


model = models.cnn((7, 8, 1), output_length)

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

model.fit(x_train, y_train, epochs=200, batch_size=30, validation_data=(x_test, y_test))"""