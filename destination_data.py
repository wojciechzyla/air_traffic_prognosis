#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple
from common_functions import standardized_hour_format, standardized_pressure_unit, standardized_visibility, \
    one_hour_time_range, check_if_in_time_range, time_difference, time_difference_range, standardized_wind_speed
import time


class DestinationData:
    def __init__(self, path_to_chromedriver:str, airport:str, date:str, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self._arrivals, self._departures, self._weather = DestinationData.get_destination_airport_data(airport=airport,date=date,path_to_chromedriver=path_to_chromedriver)
        self.dest_data = DestinationData.destination_data(arrivals=self._arrivals,departures=self._departures,weather=self._weather)

    @classmethod
    def get_destination_airport_data(cls, airport:str,date:str, path_to_chromedriver:str) -> Tuple[list,list,list]:
        path = path_to_chromedriver
        driver = webdriver.Chrome(path)

        #Go to website
        driver.get("https://www.flightradar24.com/data/airports/{}".format(airport))

        #Close cookies banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='important-banner important-banner--cookies important-banner--is-open']/div[@class='important-banner__footer']/button"))
            )
            element.click()
        except:
            pass

        #Close add banner
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='subscription-promo']/div[@id='subscription-promo-close']"))
            )
            element.click()
        except:
            pass


        #Go to arrivals
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[2]").click()
        driver.implicitly_wait(3)


        #Open hisory of past flights
        try:
            while True:
                #Check if an appropriate button is available
                btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//button[@class='btn btn-table-action btn-flights-load'][contains(text(),'Load earlier flights')]"))
                )
                btn.click()
        except:
            pass
        driver.implicitly_wait(1)


        #Find all arrivals from specific date
        arrivals_updates = driver.find_elements_by_xpath("//tr[@class='hidden-xs hidden-sm ng-scope'][@data-date='{}']".format(date))
        arrivals = []

        # Create list of dictionaries with arrival informations
        for id, arrival in enumerate(arrivals_updates):
            text_from_record = arrival.text
            data_list = text_from_record.split()

            # Check if hour is in AM/PM format or not
            if data_list[1] == "AM" or data_list[1] == "PM":
                planned_arrival = standardized_hour_format("{} {}".format(data_list[0], data_list[1]))
                flight_number = data_list[2]
            else:
                planned_arrival = standardized_hour_format(data_list[0])
                flight_number = data_list[1]

            # Find element on list containing from_airport code
            from_airport = ""
            for id_list, el in enumerate(data_list):
                if el.find("(") != -1:
                    from_airport = el[1:-1].lower()
                    break

            to_airport = airport

            # Find element on list containing aircraft registration number
            aircraft_no = ""
            for i in range(len(data_list) - 1, -1, -1):
                if data_list[i] == "Landed" or data_list[i] == "Unknown" or data_list[i] == "Canceled" or data_list[i] == "Diverted":
                    aircraft_no = data_list[i - 1].lower()
                    break

            # Check if landing time is given and if so, is it in AM/PM format or not
            if data_list[-1] == "AM" or data_list[-1] == "PM":
                landing_time = standardized_hour_format("{} {}".format(data_list[-2], data_list[-1]))
            elif data_list[-1].find(":") != -1:
                landing_time = standardized_hour_format(data_list[-1])
            else:
                landing_time = data_list[-1]

            arrivals.append(
                {"planned_arrival": planned_arrival, "flight_number": flight_number, "from_airport": from_airport,
                 "to_airport": to_airport, "aircraft_no": aircraft_no, "landing_time": landing_time})


        #Go to depeartures
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[3]").click()
        driver.implicitly_wait(3)


        #Open history of past flights
        try:
            while True:
                #Check if an appropriate button is available
                btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//button[@class='btn btn-table-action btn-flights-load'][contains(text(),'Load earlier flights')]"))
                )
                btn.click()
        except:
            pass
        driver.implicitly_wait(1)


        #Find all departures from specific date
        departures_update = driver.find_elements_by_xpath("//tr[@class='hidden-xs hidden-sm ng-scope'][@data-date='{}']".format(date))
        departures =[]

        # Create list of dictionaries with departure hour
        for id, departure in enumerate(departures_update):
            text_from_record = departure.text
            data_list = text_from_record.split()
            if data_list[1] == "AM" or data_list[1] == "PM":
                planned_departure = standardized_hour_format("{} {}".format(data_list[0], data_list[1]))
            else:
                planned_departure = standardized_hour_format(data_list[0])

            departures.append({"planned_departure": planned_departure})


        #Go to weather
        driver.find_element_by_xpath("//nav[@class='btn-group btn-block'][@role='group']/a[7]").click()
        months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                  "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
        #Date in format month-day
        date_to_num = months[date.split()[1]] + "-" + date.split()[2]
        driver.implicitly_wait(2)


        #Get all weather updates from specific date
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
        return arrivals,departures,weather


    @classmethod
    def destination_data(cls, arrivals, departures, weather):
        dest_data = []
        previously_earliest_departure = 0
        previously_earliest_weather = len(weather) - 1

        for id, arriv in enumerate(arrivals):

            # Consider only aircrafts with registration number and landing time available
            if arriv["aircraft_no"].find("(") != -1 and arriv["landing_time"].find(":") != -1:
                arriv["aircraft_no"] = arriv["aircraft_no"][arriv["aircraft_no"].find("(")+1:arriv["aircraft_no"].find(")")]
                early_hour, late_hour = one_hour_time_range(arriv["planned_arrival"])
                traffic_arrival = 0
                wind_direction_arrival = 0
                wind_speed_arrival = 0
                temperature_arrival = 0
                dew_point_arrival = 0
                pressure_arrival = 0
                visibility_arrival = 0

                # Count aircrafts arriving before current arriv within -30 minutes range
                for i in range(id - 1, -1, -1):
                    if check_if_in_time_range(early_hour, late_hour, arrivals[i]["planned_arrival"]):
                        traffic_arrival += 1
                    else:
                        break

                # Count aircrafts arriving after current arriv within +30 minutes range
                for i in range(id + 1, len(arrivals)):
                    if check_if_in_time_range(early_hour, late_hour, arrivals[i]["planned_arrival"]):
                        traffic_arrival += 1
                    else:
                        break

                # Count aircrafts departing in time range <early_hour;late_hour>
                traffic_was_added = False
                amount_added = 0
                for i in range(previously_earliest_departure, len(departures)):

                    if check_if_in_time_range(early_hour, late_hour, departures[i]["planned_departure"]):

                        if amount_added == 0:
                            previously_earliest_departure = i
                        traffic_arrival += 1
                        amount_added = 1
                        traffic_was_added = True

                    elif check_if_in_time_range(late_hour, departures[len(departures) - 1]["planned_departure"],departures[i]["planned_departure"]):

                        if not traffic_was_added:
                            previously_earliest_departure = i
                        break

                # Check weather for each plane. If there are a few weather records in time range then calculate the arithmetic mean for each
                # weather factor. If there are no weather records within the time range the calculate the arthimetic mean for two closest records
                matching_weather_counter = 0
                weather_was_added = False
                for i in range(previously_earliest_weather, -1, -1):

                    if check_if_in_time_range(early_hour, late_hour, weather[i]["time"]):

                        if matching_weather_counter == 0:
                            previously_earliest_weather = i

                        matching_weather_counter += 1
                        wind_direction_arrival += int(weather[i]["wind_direction_arrival"])
                        wind_speed_arrival += int(weather[i]["wind_speed_arrival"])
                        temperature_arrival += int(weather[i]["temperature_arrival"])
                        dew_point_arrival += int(weather[i]["dew_point_arrival"])
                        pressure_arrival += int(weather[i]["pressure_arrival"])
                        visibility_arrival += int(weather[i]["visibility_arrival"])

                        weather_was_added = True

                    elif (weather[0]["time"] >= late_hour) and (check_if_in_time_range(late_hour, weather[0]["time"], weather[i]["time"])):

                        if not weather_was_added:
                            previously_earliest_weather = i

                            matching_weather_counter = 1
                            wind_direction_arrival = int(weather[i]["wind_direction_arrival"])
                            wind_speed_arrival = int(weather[i]["wind_speed_arrival"])
                            temperature_arrival = int(weather[i]["temperature_arrival"])
                            dew_point_arrival = int(weather[i]["dew_point_arrival"])
                            pressure_arrival = int(weather[i]["pressure_arrival"])
                            visibility_arrival = int(weather[i]["visibility_arrival"])

                            if i > 0:
                                matching_weather_counter = 2
                                wind_direction_arrival += int(weather[i - 1]["wind_direction_arrival"])
                                wind_speed_arrival += int(weather[i - 1]["wind_speed_arrival"])
                                temperature_arrival += int(weather[i - 1]["temperature_arrival"])
                                dew_point_arrival += int(weather[i - 1]["dew_point_arrival"])
                                pressure_arrival += int(weather[i - 1]["pressure_arrival"])
                                visibility_arrival += int(weather[i - 1]["visibility_arrival"])
                        break

                    elif check_if_in_time_range(weather[0]["time"], late_hour, weather[i]["time"]):

                        matching_weather_counter = 1
                        wind_direction_arrival = int(weather[i]["wind_direction_arrival"])
                        wind_speed_arrival = int(weather[i]["wind_speed_arrival"])
                        temperature_arrival = int(weather[i]["temperature_arrival"])
                        dew_point_arrival = int(weather[i]["dew_point_arrival"])
                        pressure_arrival = int(weather[i]["pressure_arrival"])
                        visibility_arrival = int(weather[i]["visibility_arrival"])

                        break
                if matching_weather_counter == 0:
                    continue

                wind_direction_arrival /= matching_weather_counter
                wind_speed_arrival /= matching_weather_counter
                temperature_arrival /= matching_weather_counter
                dew_point_arrival /= matching_weather_counter
                pressure_arrival /= matching_weather_counter
                visibility_arrival /= matching_weather_counter

                landing_time_difference = time_difference_range(time_difference(arriv["planned_arrival"], arriv["landing_time"]))

                flight_data = {}
                for key, value in arriv.items():
                    flight_data[key] = value

                flight_data["arrival_traffic"] = traffic_arrival
                flight_data["wind_direction_arrival"] = int(wind_direction_arrival)
                flight_data["wind_speed_arrival"] = int(wind_speed_arrival)
                flight_data["temperature_arrival"] = int(temperature_arrival)
                flight_data["dew_point_arrival"] = int(dew_point_arrival)
                flight_data["pressure_arrival"] = int(pressure_arrival)
                flight_data["visibility_arrival"] = int(visibility_arrival)
                flight_data["landing_time_difference"] = int(landing_time_difference)

                dest_data.append(flight_data)
        return dest_data