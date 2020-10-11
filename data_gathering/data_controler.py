#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import data_gathering.destination_data as dd
import data_gathering.origin_data as od
from data_gathering.runways_coordinates import get_runways_and_distance
from datetime import datetime


def data_controler(date: str, file_name: str):

    pth = "/Applications/chromedriver"

    airports_list = []
    with open('airports.txt') as f:
        for x in f:
            codes = x.split()
            for el in codes:
                airports_list.append(el)

    # List for storing all unique origin airports
    origin_airports = []

    # List for storing codes of all unique origin airports
    origin_airports_codes = []

    # List for storing new flights
    #new_flights = []

    try:
        with open("json/this_day_airports.json","r") as file:
            data = json.load(file)
            for el in data:
                origin_airports_codes.append(el["airport"])
                origin_airports.append(el)
    except:
        print("No origin airport data from this day")


    for arpt in airports_list:
        now = datetime.now()
        if now.hour == 21 and now.minute >= 10:
            break
        try:
            # Create arrival_airport object
            arrival_airport = dd.DestinationData(pth, arpt, date)

            # Get info about airplanes arriving to destination
            destination_data = arrival_airport.dest_data
        except:
            continue

        # Loop through arriving flights
        for dest in destination_data:
            try:
                # Cerate origin_airport object
                origin_airport = od.OriginData("/Applications/chromedriver", dest["aircraft_no"], dest["flight_number"],
                                                   dest["planned_arrival"], date)

                    # Check if origin airport has already occured
                if dest["from_airport"] in origin_airports_codes:

                        # Find airport with specific code and assign apropriate data
                     for el in origin_airports:
                        if el["airport"] == dest["from_airport"]:
                            arrivals = el["arrivals"]
                            departures = el["departures"]
                            weather = el["weather"]
                            break

                else:
                        # If origin airport hasn't occured, get this data from origin_airport.get_from_web() method.
                        # Then add origin airport to origin_airports_codes and origin_airports
                    arrivals, departures, weather = origin_airport.get_from_web()
                    origin_airports_codes.append(dest["from_airport"])
                    origin_airports.append({"airport": dest["from_airport"], "arrivals": arrivals, "departures": departures,
                                                "weather": weather})

                        # Save this data to json file
                    try:
                        with open("json/this_day_airports.json","r+") as file:
                            data = json.load(file)
                            data += [{"airport":dest["from_airport"], "arrivals":arrivals, "departures":departures, "weather":weather}]
                            file.seek(0)
                            json.dump(data, file)
                    except:
                        with open("json/this_day_airports.json", "w") as file:
                            json.dump([{"airport":dest["from_airport"], "arrivals":arrivals, "departures":departures, "weather":weather}], file)

                    # Get data for specific flight from origin airport
                    origin_data = origin_airport.get_origin_data(arrivals=arrivals, departures=departures,
                                                                 weather_departure=weather)

                # Update flight info with data from origin airport
                dest.update(origin_data)
            except:
                continue

            # Update flight info with data from runways_coordinates module
            try:
                new_flights = get_runways_and_distance(pth, [dest])
            except:
                continue
            try:
                with open("json/{}".format(file_name), "r+") as file:
                    data = json.load(file)
                    data += new_flights
                    file.seek(0)
                    json.dump(data, file)
            except json.JSONDecodeError:
                with open("json/{}".format(file_name), "w") as file:
                    json.dump(new_flights, file)
            print(dest)
