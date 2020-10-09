#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import Tuple
import geopy.distance


# It there is a letter in runway directoin, return it without a letter
def runway_direction(runway: str) -> str:
    if re.search('[^0-9]', runway[-1]):
        result = runway[:runway.find("{}".format(re.findall('[^0-9]', runway)[0]))]
    else:
        result = runway
    return result


# Convert degrees, minutes, seconds format to degrees
def standardized_coordinates(latitude: str, longitude: str) -> Tuple:
    lat_deg = latitude[:latitude.find("\u00b0")]
    lat_min = latitude[latitude.find("\u00b0") + 1:latitude.find("\u2032")]
    lat_sec = latitude[latitude.find("\u2032") + 1:latitude.find("\u2033")]
    lat_hemisphere = latitude[-1]

    lat = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
    if lat_hemisphere == "S":
        lat = -lat

    lon_deg = longitude[:longitude.find("\u00b0")]
    lon_min = longitude[longitude.find("\u00b0") + 1:longitude.find("\u2032")]
    lon_sec = longitude[longitude.find("\u2032") + 1:longitude.find("\u2033")]
    lon_hemisphere = longitude[-1]

    lon = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600
    if lon_hemisphere == "W":
        lon = -lon

    return lat, lon


def runways_coordinates(path_to_chromedriver: str, airports_codes: list, airports: list) -> list:
    path = path_to_chromedriver
    driver = webdriver.Chrome(path)

    for airport in airports_codes:

        # Try to find airport by entering it's code. If it fails then go to flightradar24 and get full name of airport
        try:
            # Go to google
            driver.get("https://www.google.com/")
            text_to_search = "{} airport wikipedia".format(airport)
            input_box = driver.find_element_by_xpath("//input[@class='gLFyf gsfi']")
            input_box.clear()
            input_box.send_keys(text_to_search)
            input_box.send_keys(Keys.ENTER)

            driver.find_element_by_xpath("//div[@class='rc'][1] / div / a").click()

            # Find latitude and longitude of airport
            latitude = driver.find_element_by_class_name("latitude").text
            longitude = driver.find_element_by_class_name("longitude").text

            # Get all the runways available on the wikipedia website
            runways = driver.find_elements_by_xpath(
                "//tr[th/a/span[contains(text(),'Runways')]] / following-sibling::tr[1] / td / table / tbody / tr[td]")
            filtered_runways = []


        except:
            try:
                # Go to wikipedia
                driver.get("https://www.wikipedia.org/")
                text_to_search = "{} airport".format(airport)
                input_box = driver.find_element_by_id("searchInput")
                input_box.clear()
                input_box.send_keys(text_to_search)
                driver.implicitly_wait(1)
                input_box.send_keys(Keys.ENTER)

                driver.implicitly_wait(2)

                # Find latitude and longitude of airport
                latitude = driver.find_element_by_class_name("latitude").text
                longitude = driver.find_element_by_class_name("longitude").text

                # Get all the runways available on the wikipedia website
                runways = driver.find_elements_by_xpath(
                    "//tr[th/a/span[contains(text(),'Runways')]] / following-sibling::tr[1] / td / table / tbody / tr[td]")
                filtered_runways = []

            except:
                driver.get("https://www.flightradar24.com/data/airports/{}".format(airport))
                text_to_search = driver.find_element_by_class_name("airport-name").text

                # Go to wikipedia
                driver.get("https://en.wikipedia.org/wiki/Main_Page")

                input_box = driver.find_element_by_id("searchInput")
                input_box.send_keys(text_to_search)
                driver.implicitly_wait(1)
                driver.find_element_by_xpath("//div [@class='suggestions-results'] / a[1]").click()

                driver.implicitly_wait(2)

                # Find latitude and longitude of airport
                latitude = driver.find_element_by_class_name("latitude").text
                longitude = driver.find_element_by_class_name("longitude").text

                # Get all the runways available on the wikipedia website
                runways = driver.find_elements_by_xpath(
                    "//tr[th/a/span[contains(text(),'Runways')]] / following-sibling::tr[1] / td / table / tbody / tr[td]")
                filtered_runways = []


        # Filter only concrete/asphalt runways and get their directions
        for run in runways:
            run_list = run.text.split()
            if run_list[-1].lower().find("asphalt") != -1 or run_list[-1].lower().find("concrete") != -1:
                slash = run_list[0].find("/")
                filtered_runways.append(runway_direction(run_list[0][:slash]))
                filtered_runways.append(runway_direction(run_list[0][slash + 1:]))

        # Add latitude and longitude to the airport as well as all runways directions
        for el in airports:
            if el["code"] == airport:
                latitude, longitude = standardized_coordinates(str(latitude), str(longitude))
                el["latitude"] = latitude
                el["longitude"] = longitude

                for i in range(0, 18):
                    el["runway {}".format(i)] = filtered_runways[i] if i < len(filtered_runways) else -1

    driver.quit()

    return airports


def update_flight_info(flights_json_data: list, airports: list) -> list:
    for flight in flights_json_data:

        for air in airports:
            if air["code"] == flight["from_airport"]:
                lat1 = air["latitude"]
                lon1 = air["longitude"]
                coor1 = (lat1, lon1)
                flight["from latitude"] = lat1
                flight["from longitude"] = lon1

                for i in range(0, 18):
                    flight["from runway {}".format(i)] = int(air["runway {}".format(i)])

            if air["code"] == flight["to_airport"]:
                lat2 = air["latitude"]
                lon2 = air["longitude"]
                coor2 = (lat2, lon2)
                flight["to latitude"] = lat2
                flight["to longitude"] = lon2

                for i in range(0, 18):
                    flight["to runway {}".format(i)] = int(air["runway {}".format(i)])

        flight["distance"] = geopy.distance.GreatCircleDistance(coor1, coor2).km

    return flights_json_data


def get_runways_and_distance(path_to_chromedriver:str, flights_json_data:list):
    airports_codes = []
    airports = []
    # Try to read from airport_data.json
    try:
        with open("json/airport_data.json", "r") as file:
            airports = json.load(file)

            # Add codes to airports_codes
            for air in airports:
                airports_codes.append(air["code"])

        new_airports = []
        new_airports_codes = []

        # Add airports to new_airports and new_airports_codes if they weren't added from airport_data.json
        for el in flights_json_data:
            if el["from_airport"] not in airports_codes:
                new_airports_codes.append(el["from_airport"])
                new_airports.append({"code": el["from_airport"]})
            if el["to_airport"] not in airports_codes:
                new_airports_codes.append(el["to_airport"])
                new_airports.append({"code": el["to_airport"]})

        if len(new_airports) > 0:
            airports += runways_coordinates(path_to_chromedriver, new_airports_codes, new_airports)
            airports_codes += new_airports_codes

        del new_airports_codes
        del new_airports

        flights_json_data = update_flight_info(flights_json_data, airports)

        # Try to write to airport_data.json
        try:
            with open("json/airport_data.json", "w") as file:
                file.seek(0)
                json.dump(airports, file)
        except:
            print("Couldn't write to airport_data")

        return flights_json_data


    except json.JSONDecodeError:

        # Add destination airport to airports and airports_codes
        airports.append({"code": flights_json_data[0]["to_airport"]})
        airports_codes.append(flights_json_data[0]["to_airport"])

        # Add airports to airports and airports_codes if they are not there already
        for el in flights_json_data:
            if el["from_airport"] not in airports_codes:
                airports_codes.append(el["from_airport"])
                airports.append({"code": el["from_airport"]})
                airports = runways_coordinates(path_to_chromedriver, airports_codes, airports)
            if el["to_airport"] not in airports_codes:
                airports_codes.append(el["to_airport"])
                airports.append({"code": el["to_airport"]})
                airports = runways_coordinates(path_to_chromedriver, airports_codes, airports)


        flights_json_data = update_flight_info(flights_json_data, airports)

        # Try to write to airport_data.json
        try:
            with open("json/airport_data.json", "w") as file:
                json.dump(airports, file)
        except:
            print("Couldn't write to airport_data.json")

    return flights_json_data