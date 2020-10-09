#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import common_functions as cf


class TestFunctions(unittest.TestCase):

    def test_standardized_pressure_unit(self):
        self.assertEqual(cf.standardized_pressure_unit("1023 hPa", "lhr"), "1023")
        self.assertEqual(cf.standardized_pressure_unit("30.13 inHg", "mdw"), "1020")
        self.assertRaises(cf.UnknownPressureUnitError, cf.standardized_pressure_unit, "30.13 qqq", "mdw")

    def test_standardized_visibility(self):
        self.assertEqual(cf.standardized_visibility("10 SM", "mdw"), "9999")
        self.assertEqual(cf.standardized_visibility("5 SM", "mdw"), "8046")
        self.assertEqual(cf.standardized_visibility("9999 m", "cdg"), "9999")
        self.assertRaises(cf.UnknownLengthUnitError, cf.standardized_visibility, "30 q", "mdw")

    def test_standardized_hour_format(self):
        self.assertEqual(cf.standardized_hour_format("12:34 AM"), "00:34")
        self.assertEqual(cf.standardized_hour_format("2:34 AM"), "02:34")
        self.assertEqual(cf.standardized_hour_format("06:14 AM"), "06:14")
        self.assertEqual(cf.standardized_hour_format("12:03 PM"), "12:03")
        self.assertEqual(cf.standardized_hour_format("4:34 PM"), "16:34")
        self.assertEqual(cf.standardized_hour_format("12:34"), "12:34")
        self.assertEqual(cf.standardized_hour_format("04:49"), "04:49")
        self.assertEqual(cf.standardized_hour_format("23:00"), "23:00")

    def test_hour_in_pmam_format(self):
        self.assertEqual(cf.hour_in_pmam_format("00:11"), "12:11 AM")
        self.assertEqual(cf.hour_in_pmam_format("06:00"), "6:00 AM")
        self.assertEqual(cf.hour_in_pmam_format("11:11"), "11:11 AM")
        self.assertEqual(cf.hour_in_pmam_format("10:59"), "10:59 AM")
        self.assertEqual(cf.hour_in_pmam_format("14:31"), "2:31 PM")

    def test_return_full_hour_format(self):
        self.assertEqual(cf.return_full_hour_format("5"), "05")
        self.assertEqual(cf.return_full_hour_format("50"), "50")

    def test_one_hour_time_range(self):
        self.assertEqual(cf.one_hour_time_range("00:23"), ("00:00", "00:53"))
        self.assertEqual(cf.one_hour_time_range("02:30"), ("02:00", "03:00"))
        self.assertEqual(cf.one_hour_time_range("15:13"), ("14:43", "15:43"))
        self.assertEqual(cf.one_hour_time_range("21:42"), ("21:12", "22:12"))
        self.assertEqual(cf.one_hour_time_range("08:00"), ("07:30", "08:30"))
        self.assertEqual(cf.one_hour_time_range("23:37"), ("23:07", "23:59"))

    def test_check_if_in_time_range(self):
        self.assertTrue(cf.check_if_in_time_range("03:45", "04:45", "03:45"))
        self.assertTrue(cf.check_if_in_time_range("12:21", "13:21", "12:45"))
        self.assertTrue(cf.check_if_in_time_range("07:45", "08:45", "08:45"))
        self.assertTrue(cf.check_if_in_time_range("22:03", "23:03", "23:00"))
        self.assertTrue(cf.check_if_in_time_range("12:45", "12:48", "12:46"))
        self.assertFalse(cf.check_if_in_time_range("22:03", "23:03", "23:10"))
        self.assertFalse(cf.check_if_in_time_range("15:03", "16:03", "10:10"))

    def test_time_difference(self):
        self.assertEqual(cf.time_difference("23:58", "00:23"), 25)
        self.assertEqual(cf.time_difference("00:07", "23:23"), -44)
        self.assertEqual(cf.time_difference("12:18", "12:18"), 0)
        self.assertEqual(cf.time_difference("23:58", "23:00"), -58)
        self.assertEqual(cf.time_difference("07:38", "8:07"), 29)

    def test_ime_difference_range(self):
        self.assertEqual(cf.time_difference_range(-73), 0)
        self.assertEqual(cf.time_difference_range(-60), 1)
        self.assertEqual(cf.time_difference_range(-51), 1)
        self.assertEqual(cf.time_difference_range(-21), 2)
        self.assertEqual(cf.time_difference_range(-10), 3)
        self.assertEqual(cf.time_difference_range(-0), 4)
        self.assertEqual(cf.time_difference_range(19), 5)
        self.assertEqual(cf.time_difference_range(28), 6)
        self.assertEqual(cf.time_difference_range(51), 7)
        self.assertEqual(cf.time_difference_range(83), 8)
        self.assertEqual(cf.time_difference_range(90), 8)
        self.assertEqual(cf.time_difference_range(91), 9)

    def test_standardized_coordinates(self):
        self.assertAlmostEqual(cf.standardized_coordinates("51°30′19″N", "000°03′19″E")[0], 51.505278, places=2)
        self.assertAlmostEqual(cf.standardized_coordinates("51°30′19″N", "000°03′19″E")[1], 0.055278, places=2)
        self.assertAlmostEqual(cf.standardized_coordinates("51°30′19″S", "000°03′19″W")[0], -51.505278, places=2)
        self.assertAlmostEqual(cf.standardized_coordinates("51°30′19″S", "000°03′19″W")[1], -0.055278, places=2)

    def test_standardized_wind_speed(self):
        self.assertEqual(cf.standardized_wind_speed("12kt"), "12")
        self.assertEqual(cf.standardized_wind_speed("2m/s"), "4")
        self.assertRaises(cf.UnknownSpeedUnitError, cf.standardized_wind_speed, "30ft/h")


if __name__ == "__main__":
    unittest.main()
