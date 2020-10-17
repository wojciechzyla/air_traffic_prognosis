#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import wraps
from typing import Callable
from datetime import datetime
from data_gathering.common_functions import standardized_hour_format, hour_in_pmam_format, time_difference, time_difference_range,\
    one_hour_time_range, check_if_in_time_range, standardized_pressure_unit, standardized_visibility, standardized_wind_speed


def time_difference_decorator(func:Callable) -> Callable:
    @wraps(func)
    def func_wrapper(departure:str,arrival:str) -> int:
        fmt = "%H:%M"
        arriv = datetime.strptime(arrival, fmt)
        dep = datetime.strptime(departure, fmt)
        if arriv <= dep:
            difference = str(arriv-dep).split()[2]
            hours = difference[:difference.find(":")]
            minutes = difference[difference.find(":")+1:difference.find(":")+3]
            result = 60*int(hours)+int(minutes)
        else:
            result = func(departure, arrival)
        return result
    return func_wrapper


def time_difference_range_decorator(func:Callable) -> Callable:
    @wraps(func)
    def func_wrapper(time_diff:int) -> int:
        if time_diff <= 5:
            result = 4
        else:
            result = func(time_diff)
        return result
    return func_wrapper


class OriginData:
    def __init__(self,path_to_chromedriver:str, aircraft_no:str, flight_number:str, planned_arrival:str, date:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_to_chromedriver = path_to_chromedriver
        self.aircraft_no = aircraft_no
        self.flight_number = flight_number
        self.planned_arrival = planned_arrival
        self.date = date


    def get_from_web(self):
        path_to_chromedriver =  self.path_to_chromedriver
        aircraft_no = self.aircraft_no
        flight_number = self.flight_number
        planned_arrival = self.planned_arrival
        date = self.date

        path = path_to_chromedriver
        driver = webdriver.Chrome(path)

        # Go to website with aircraft flight history
        driver.get("https://www.flightradar24.com/data/aircraft/{}".format(aircraft_no))

        # Close cookies banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//div[@class='important-banner important-banner--cookies important-banner--is-open']/div[@class='important-banner__footer']/button"))
            )
            element.click()
        except:
            pass

        # Close add banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='subscription-promo']/div[@id='subscription-promo-close']"))
            )
            element.click()
        except:
            pass

        # Get origin airport code
        airport = driver.find_element_by_xpath("//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / td[4] / a"
                                               .format(flight_number,planned_arrival)).text[1:-1].lower()

        # Go to origin airport website
        driver.find_element_by_xpath("//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / td[4] / a".format(flight_number,planned_arrival)).click()

        # Go to arrivals
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[2]").click()
        driver.implicitly_wait(1)

        # Open hisory of past flights
        try:
            while True:
                # Check if an appropriate button is available
                btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//button[@class='btn btn-table-action btn-flights-load'][contains(text(),'Load earlier flights')]"))
                )
                btn.click()
        except:
            pass
        driver.implicitly_wait(1)

        # Get list of all arrivals at origin airport during specified day
        arrivals_updates = driver.find_elements_by_xpath("//tr[@class='hidden-xs hidden-sm ng-scope'][@data-date='{}']".format(date))
        arrivals = []

        # Create a list with dictionaries with arrival information
        for id, arrival in enumerate(arrivals_updates):
            text_from_record = driver.find_element_by_xpath("//tr[@class='hidden-xs hidden-sm ng-scope'][@data-date='{}'][{}]".format(date, id + 1)).text
            data_list = text_from_record.split()
            if data_list[1] == "AM" or data_list[1] == "PM":
                arrival_hour = standardized_hour_format("{} {}".format(data_list[0], data_list[1]))
            else:
                arrival_hour = standardized_hour_format(data_list[0])

            arrivals.append({"arrival_hour":arrival_hour})

        # Go to depeartures
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[3]").click()
        driver.implicitly_wait(3)

        # Open history of past flights
        try:
            while True:
                # Check if an appropriate button is available
                btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//button[@class='btn btn-table-action btn-flights-load'][contains(text(),'Load earlier flights')]"))
                )
                btn.click()
        except:
            pass
        driver.implicitly_wait(1)

        # Get list of all departures at origin airport during specified day
        departures_update = driver.find_elements_by_xpath("//tr[@class='hidden-xs hidden-sm ng-scope'][@data-date='{}']".format(date))
        departures = []

        # Create list of dictionaries with departure hour
        for id, departure in enumerate(departures_update):
            text_from_record = departure.text
            data_list = text_from_record.split()

            if data_list[1] == "AM" or data_list[1] == "PM":
                planned_departure = standardized_hour_format("{} {}".format(data_list[0], data_list[1]))
            else:
                planned_departure = standardized_hour_format(data_list[0])

            departures.append({"departure_hour": planned_departure})

        # Go to weather
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[7]").click()
        months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
                  "Aug": "08","Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
        # Date in format month-day
        date_to_num = months[date.split()[1]] + "-" + date.split()[2]
        driver.implicitly_wait(2)

        # Get all weather updates from specific date
        weather_updates = driver.find_elements_by_xpath("//tr[@class='master expandable']/td[2][contains(text(),'{}')]".format(date_to_num))
        weather = []

        # Create list of dictionaries with weather information
        for id, weather_update in enumerate(weather_updates):
            weather_update.click()
            driver.implicitly_wait(2)
            path_to_weather_details = "//tr[@class='slave'][@style='display: table-row;'][{}]".format(id + 1)
            text_from_record = driver.find_element_by_xpath(path_to_weather_details).text
            data_list = text_from_record.split()

            day = date_to_num
            hour = data_list[3]

            if len(data_list) >= 20:
                # Weather update with wind direction and without wind gust
                if data_list[6].find("direction") != -1 and data_list[19].find("Visibility") != -1:
                    wind_direction = data_list[7][:-1]
                    wind_speed = standardized_wind_speed(data_list[10])
                    temperature = data_list[12][:-2]
                    dew_point = data_list[15][:-2]
                    pressure = standardized_pressure_unit("{} {}".format(data_list[17], data_list[18]), airport)
                    vis = data_list[-1]
                    visibility = standardized_visibility("{} {}".format(data_list[-2], data_list[-1]),
                                                         airport) if vis != "OK" else "9999"
                    weather.append({"day": day, "time": hour, "wind_direction_arrival": wind_direction,
                                    "wind_speed_arrival": wind_speed,
                                    "temperature_arrival": temperature, "dew_point_arrival": dew_point,
                                    "pressure_arrival": pressure, "visibility_arrival": visibility})

                # Weather update with wind direction and with wind gust
                elif data_list[6].find("direction") != -1 and data_list[12].find("gust") != -1:
                    wind_direction = data_list[7][:-1]
                    wind_speed = standardized_wind_speed(data_list[10])
                    temperature = data_list[15][:-2]
                    dew_point = data_list[18][:-2]
                    pressure = standardized_pressure_unit("{} {}".format(data_list[20], data_list[21]), airport)
                    vis = data_list[-1]
                    visibility = standardized_visibility("{} {}".format(data_list[-2], data_list[-1]),
                                                         airport) if vis != "OK" else "9999"
                    weather.append({"day": day, "time": hour, "wind_direction_arrival": wind_direction,
                                    "wind_speed_arrival": wind_speed,
                                    "temperature_arrival": temperature, "dew_point_arrival": dew_point,
                                    "pressure_arrival": pressure, "visibility_arrival": visibility})

        driver.quit()

        return arrivals, departures, weather



    def get_origin_data(self, arrivals:list, departures:list, weather_departure:list):
        path_to_chromedriver =self.path_to_chromedriver
        aircraft_no = self.aircraft_no
        flight_number = self.flight_number
        planned_arrival =self.planned_arrival

        path = path_to_chromedriver
        driver = webdriver.Chrome(path)

        # Go to website with aircraft flight history
        driver.get("https://www.flightradar24.com/data/aircraft/{}".format(aircraft_no))

        # Close cookies banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,"//div[@class='important-banner important-banner--cookies important-banner--is-open']/div[@class='important-banner__footer']/button"))
            )
            element.click()
        except:
            pass

        # Close add banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='subscription-promo']/div[@id='subscription-promo-close']"))
            )
            element.click()
        except:
            pass


        #Find record with desired flight
        try:
            #Try to find fligh using stnadard hour format
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / td[8]".format(flight_number, planned_arrival)))
            )
            planned_departure = standardized_hour_format(element.text)
        except:
            try:
                #Try to find flight using PM/AM hour format
                time_in_ampm = hour_in_pmam_format(planned_arrival)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / td[8]".format(flight_number, time_in_ampm)))
                )
                planned_departure = standardized_hour_format(element.text)
            except:
                raise ValueError("Didn't find departure hour for flight number {} for aircraft {}".format(flight_number,aircraft_no))


        #Decorate recived time_difference function so that it calculates flight duration. (NOT USED)
        #flight_duration = time_difference_decorator(time_difference)
        #planned_duration = flight_duration(planned_departure, planned_arrival)


        #Get planned and actual arrival time from previous flight
        planned_arrival_at_origin = driver.find_element_by_xpath("//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / following-sibling::tr / td[10]".format(flight_number, planned_arrival)).text
        arrival_at_origin = driver.find_element_by_xpath("//tr [td/a[contains(text(),'{}')]] [td[contains(text(),'{}')]] / following-sibling::tr / td[12]".format(flight_number, planned_arrival)).text

        #Check if planned arrival time at origin was given. If not, it's assumed it wasn't delayed, that's why both hours have the same value.
        if ":" in planned_arrival_at_origin:
            #Check if actual landing time was given. If not, it's assumed flight wasn't delayed, that's why both hours have the same value.
            planned_arrival_at_origin = standardized_hour_format(planned_arrival_at_origin)
            if "Landed" in arrival_at_origin:
                arrival_at_origin = standardized_hour_format(arrival_at_origin[7:])
            else:
                arrival_at_origin = planned_arrival_at_origin
        else:
            planned_arrival_at_origin = "00:00"
            arrival_at_origin = planned_arrival_at_origin

        # Decorate time_difference_range function so that earlier arrival is considered as on time arrival
        what_delay = time_difference_range_decorator(time_difference_range)

        # Check if aircraft was delayed during previous flight
        previous_delay = what_delay(time_difference(planned_arrival_at_origin,arrival_at_origin)) #To return

        # Calculate time range <planned_departure-30 minutes ; planned_departure-30 minutes>
        early_hour, late_hour = one_hour_time_range(planned_departure)

        traffic_departure = 0 # Variable to store traffic during departure


        #Count all arrivals during specified time range
        for id, arriv in enumerate(arrivals):
            arrival_hour = arriv["arrival_hour"]
            if check_if_in_time_range(early_hour, late_hour, arrival_hour):
                traffic_departure += 1

        # Count all departures during specified time range
        for id, departure in enumerate(departures):
            departure_hour = departure["departure_hour"]
            if check_if_in_time_range(early_hour,late_hour,departure_hour):
                traffic_departure += 1

        # One must be deducted from traffic, because during departures calculations
        # our flight was also included
        if traffic_departure > 0:
            traffic_departure -= 1

        wind_direction_departure = 0
        wind_speed_departure = 0
        temperature_departure = 0
        dew_point_departure = 0
        pressure_departure = 0
        visibility_departure = 0

        # Check weather. If there are a few weather records in time range then calculate the arithmetic mean for each
        # weather factor. If there are no weather records within the time range the calculate the arthimetic mean for two closest records
        matching_weather_counter = 0
        weather_was_added = False

        for i in range(len(weather_departure)-1, -1, -1):

            if check_if_in_time_range(early_hour, late_hour, weather_departure[i]["time"]):

                matching_weather_counter += 1
                wind_direction_departure += int(weather_departure[i]["wind_direction_arrival"])
                wind_speed_departure += int(weather_departure[i]["wind_speed_arrival"])
                temperature_departure += int(weather_departure[i]["temperature_arrival"])
                dew_point_departure += int(weather_departure[i]["dew_point_arrival"])
                pressure_departure += int(weather_departure[i]["pressure_arrival"])
                visibility_departure += int(weather_departure[i]["visibility_arrival"])

                weather_was_added = True

            elif (weather_departure[0]["time"] >= late_hour) and (
            check_if_in_time_range(late_hour, weather_departure[0]["time"], weather_departure[i]["time"])):
                if not weather_was_added:
                    matching_weather_counter = 1
                    wind_direction_departure = int(weather_departure[i]["wind_direction_arrival"])
                    wind_speed_departure = int(weather_departure[i]["wind_speed_arrival"])
                    temperature_departure = int(weather_departure[i]["temperature_arrival"])
                    dew_point_departure = int(weather_departure[i]["dew_point_arrival"])
                    pressure_departure = int(weather_departure[i]["pressure_arrival"])
                    visibility_departure = int(weather_departure[i]["visibility_arrival"])

                    if i > 0:
                        matching_weather_counter = 2
                        wind_direction_departure += int(weather_departure[i - 1]["wind_direction_arrival"])
                        wind_speed_departure += int(weather_departure[i - 1]["wind_speed_arrival"])
                        temperature_departure += int(weather_departure[i - 1]["temperature_arrival"])
                        dew_point_departure += int(weather_departure[i - 1]["dew_point_arrival"])
                        pressure_departure += int(weather_departure[i - 1]["pressure_arrival"])
                        visibility_departure += int(weather_departure[i - 1]["visibility_arrival"])
                break

            elif check_if_in_time_range(weather_departure[0]["time"], late_hour, weather_departure[i]["time"]):

                matching_weather_counter = 1
                wind_direction_departure = int(weather_departure[i]["wind_direction_arrival"])
                wind_speed_departure = int(weather_departure[i]["wind_speed_arrival"])
                temperature_departure = int(weather_departure[i]["temperature_arrival"])
                dew_point_departure = int(weather_departure[i]["dew_point_arrival"])
                pressure_departure = int(weather_departure[i]["pressure_arrival"])
                visibility_departure = int(weather_departure[i]["visibility_arrival"])

                break

        wind_direction_departure /= matching_weather_counter
        wind_speed_departure /= matching_weather_counter
        temperature_departure /= matching_weather_counter
        dew_point_departure /= matching_weather_counter
        pressure_departure /= matching_weather_counter
        visibility_departure /= matching_weather_counter

        driver.quit()

        return {"delay_departure":previous_delay, "traffic_departure":traffic_departure,
                "wind_direction_departure":int(wind_direction_departure),"wind_speed_departure":int(wind_speed_departure),
                "temperature_departure":int(temperature_departure), "dew_point_departure":int(dew_point_departure),
                "pressure_departure":int(pressure_departure), "visibility_departure":int(visibility_departure)}