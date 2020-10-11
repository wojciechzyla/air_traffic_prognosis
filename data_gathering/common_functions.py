#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Tuple


class UnknownPressureUnitError(Exception):
    def __init__(self, airport:str):
        if airport is None:
            msg = "Unknown pressure unit"
        else:
            msg = "Unknown pressure unit at destination {} airport".format(airport)
        super().__init__(msg)


class UnknownLengthUnitError(Exception):
    def __init__(self, airport:str):
        if airport is None:
            msg = "Unknown length unit"
        else:
            msg = "Unknown length unit at destination {} airport".format(airport)
        super().__init__(msg)


class UnknownSpeedUnitError(Exception):
    def __init__(self, u:str):
        msg = "Unknown speed unit {}".format(u)
        super().__init__(msg)


# Return pressure in hPa
def standardized_pressure_unit(pressure:str, airport:str) -> str:
    if pressure.find("hPa") != -1:
        result = pressure[:-4]
    elif pressure.find("inHg") != -1:
        result =str(int(33.86 * float(pressure[:-5])))
    else:
        print("error {}".format(pressure))
        raise UnknownPressureUnitError(airport)
    return result


# Return visibility in meters
def standardized_visibility(visibility:str, airport:str) -> str:
    if visibility[-2:] == "SM":
        vis = int(1609.34 * float(visibility[:-3]))
        result = str(vis) if vis <= 9999 else "9999"
    elif visibility[-2:] == " m":
        result = visibility[:-2]
    else:
        raise UnknownLengthUnitError(airport)
    return result


# Return hour in 24h format
def standardized_hour_format(hour:str) -> str:
    hours = {"12": "12", "1": "13", "2": "14", "3": "15", "4": "16", "5": "17", "6": "18", "7": "19", "8": "20",
             "9": "21", "10": "22", "11": "23"}
    if hour.find("PM") != -1:
        result = hours[hour[:hour.find(":")]] + hour[hour.find(":"):-3]
    elif hour.find("AM") != -1:
        if hour[:hour.find(":")] == "12":
            result = "00" + hour[hour.find(":"):-3]
        else:
            result = hour[:-3] if len(hour[:hour.find(":")]) == 2 else "0" + hour[:-3]
    else:
        result = hour
    return result


# Return hour in PM/AM format
def hour_in_pmam_format(hour:str) -> str:
    am_double_hours = ["10", "11"]
    pm_hours = {"12":"12", "13":"1", "14":"2", "15":"3", "16":"4", "17":"5", "18":"6", "19":"7", "20":"8", "21":"9", "22":"10", "23":"11"}
    if hour[0] == "0":
        if hour[1] == "0":
            result = "12" + hour[2:] + " AM"
        else:
            result = hour[1:] + " AM"
    elif hour[0:2] in am_double_hours:
        result = hour + " AM"
    else:
        result = pm_hours[hour[:2]] + ":" + hour[3:] + " PM"
    return result


# Function return_full_hour_format() is used while making computations on hours. For example,
# if minutes in hour 12:36 are converted to int type,
# then 30 minutes are deducted and then it is converted back to str type, result will be 12:6.
# This function recives that 6 and changes it into 06.
def return_full_hour_format(hour_or_minutes:str) -> str:
    if len(hour_or_minutes) == 1:
        result = "0" + hour_or_minutes
    else:
        result = hour_or_minutes
    return result


# Return range <hour-30 minutes ; hour+30 minutes>
# Minimium value for hour-30 minutes is 00:00
# Maximum value for hour+30 minutes is 23:59
def one_hour_time_range(hour:str) -> Tuple[str,str]:
    hours = hour[:hour.find(":")] #Extracted hour from hour
    minutes = hour[hour.find(":")+1:] #Extracted minutes from hour
    if int(minutes) >= 30:
        early_hour = hours + ":" + return_full_hour_format(str(int(minutes) - 30))
        if hours != "23":
            late_hour = return_full_hour_format(str(int(hours) + 1)) + ":" + return_full_hour_format(str(int(minutes) - 30))
        else:
            late_hour = "23:59"
    else:
        late_hour = hours + ":" + str(int(minutes)+30)
        if hours != "00":
            early_hour = return_full_hour_format(str(int(hours) - 1)) + ":" + return_full_hour_format(str(int(minutes) + 30))
        else:
            early_hour = "00:00"
    return early_hour,late_hour


# Check if hour is in range <early_hour;late_hour>
def check_if_in_time_range(early_hour:str,late_hour:str,hour:str) -> bool:
    erl_hr = early_hour[:early_hour.find(":")] #Extracted hour from early_hour
    erl_min = early_hour[early_hour.find(":")+1:] #Extracted minutes from early_hour
    late_hr = late_hour[:late_hour.find(":")] #Extracted hour from late_hour
    late_min = late_hour[late_hour.find(":")+1:] #Extracted minutes from late_hour
    hr = hour[:hour.find(":")] #Extracted hour from hour
    minutes = hour[hour.find(":")+1:] #Extracted minutes from hour
    bigger = False
    smaller = False
    for i in range(0,1):
        if (erl_hr == hr and int(minutes) >= int(erl_min)) or (int(hr) > int(erl_hr)):
            bigger = True
        if (late_hr == hr and int(minutes) <= int(late_min)) or (int(hr) < int(late_hr)):
            smaller = True
    return bigger and smaller


#Calculate time difference between two hours
def time_difference(planned_arrival:str, landed:str) -> int:
    fmt = "%H:%M"
    planned = datetime.strptime(planned_arrival,fmt)
    land = datetime.strptime(landed,fmt)
    if check_if_in_time_range("22:30", "23:59", planned_arrival) and check_if_in_time_range("00:00", "01:30", landed):
        helper1 = datetime.strptime("23:59", fmt)
        tdelta = helper1 - planned
        helper2 = datetime.strptime("00:00", fmt)
        tdelta += land - helper2
        hours = str(tdelta)[:str(tdelta).find(":")]
        minutes = str(tdelta)[str(tdelta).find(":") + 1:str(tdelta).find(":") + 3]
        result = int(hours) * 60 + int(minutes) + 1

    elif check_if_in_time_range("00:00", "01:30", planned_arrival) and check_if_in_time_range("22:30", "23:59", landed):
        helper1 = datetime.strptime("00:00", fmt)
        tdelta = planned - helper1
        helper2 = datetime.strptime("23:59", fmt)
        tdelta += helper2 - land
        hours = str(tdelta)[:str(tdelta).find(":")]
        minutes = str(tdelta)[str(tdelta).find(":") + 1:str(tdelta).find(":") + 3]
        result = -int(hours) * 60 - int(minutes) - 1

    elif planned >= land:
        tdelta = planned - land
        hours = str(tdelta)[:str(tdelta).find(":")]
        minutes = str(tdelta)[str(tdelta).find(":")+1:str(tdelta).find(":")+3]
        result = -int(hours)*60-int(minutes)

    else:
        tdelta = land - planned
        hours = str(tdelta)[:str(tdelta).find(":")]
        minutes = str(tdelta)[str(tdelta).find(":") + 1:str(tdelta).find(":") + 3]
        result = int(hours)*60+int(minutes)
    return result


#time_difference_range() recives difference between planned arrival and actual arrival and returns a number which corresponds to the time range
def time_difference_range(time_diff:int) -> int:
    if time_diff < -60:
        result = 0
    elif -60 <= time_diff < -40:
        result = 1
    elif -40 <= time_diff < -20:
        result = 2
    elif -20 <= time_diff <-5:
        result = 3
    elif -5 <= time_diff <= 5:
        result = 4
    elif 5 < time_diff <= 20:
        result = 5
    elif 20 < time_diff <= 40:
        result = 6
    elif 40 < time_diff <= 60:
        result = 7
    elif 60 < time_diff <= 90:
        result = 8
    else:
        result = 9
    return result


# Convert degrees, minutes, seconds format to degrees
def standardized_coordinates(latitude:str, longitude:str):
    lat_deg = latitude[:latitude.find("\u00b0")]
    lat_min = latitude[latitude.find("\u00b0")+1:latitude.find("\u2032")]
    lat_sec = latitude[latitude.find("\u2032")+1:latitude.find("\u2033")]
    lat_hemisphere = latitude[-1]

    lat = int(lat_deg) + int(lat_min) / 60 + int(lat_sec) / 3600
    if lat_hemisphere == "S":
        lat = -lat

    lon_deg = longitude[:longitude.find("\u00b0")]
    lon_min = longitude[longitude.find("\u00b0")+1:longitude.find("\u2032")]
    lon_sec = longitude[longitude.find("\u2032")+1:longitude.find("\u2033")]
    lon_hemisphere = longitude[-1]

    lon = int(lon_deg) + int(lon_min) / 60 + int(lon_sec) / 3600
    if lon_hemisphere == "W":
        lon = -lon

    return lat, lon


# Transfer wind speed from m/s to kt
def standardized_wind_speed(wind_speed:str) -> str:
    if wind_speed[-2:] == "kt":
        result = wind_speed[:-2]
    elif wind_speed[-3:] == "m/s":
        num = float(wind_speed[:-3])
        num *= 1.94
        result = str(round(num))
    else:
        raise UnknownSpeedUnitError(wind_speed)
    return result
