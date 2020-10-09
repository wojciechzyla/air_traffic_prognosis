#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import runways_coordinates as rc


class TestFunctionsWithoutWebAcces(unittest.TestCase):

    def test_runway_direction(self):
        self.assertEqual(rc.runway_direction("09L"), "09")
        self.assertEqual(rc.runway_direction("25"), "25")

    def test_standardized_coordinates(self):
        self.assertAlmostEqual(rc.standardized_coordinates("51°30′19″N", "000°03′19″E")[0], 51.505278, places=2)
        self.assertAlmostEqual(rc.standardized_coordinates("51°30′19″N", "000°03′19″E")[1], 0.055278, places=2)
        self.assertAlmostEqual(rc.standardized_coordinates("51°30′19″S", "000°03′19″W")[0], -51.505278, places=2)
        self.assertAlmostEqual(rc.standardized_coordinates("51°30′19″S", "000°03′19″W")[1], -0.055278, places=2)


if __name__ == "__main__":
    unittest.main()
