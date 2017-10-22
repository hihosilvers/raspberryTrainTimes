from __future__ import print_function
from os import environ
from time import sleep
import unicornhat as unicorn
from datetime import datetime
from pytz import timezone
from sys import exit
from nrewebservices.ldbws import Session
from urllib.error import URLError
import coordinates

####################################################################################################
# Load the configuration.

# Set up the address for the LDBWS server.
API_URL = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-02-02"

# Get the API key from the environment
try:
    API_KEY = environ['NRE_LDBWS_API_KEY']
    FROM_STATION = environ['FROM_STATION']
    TO_STATION = environ['TO_STATION']
except KeyError:
    print()
    print("To run this example you need to set the environment variable NRE_LDBWS_API_KEY to your")
    print("NRE OpenLDBWS API Key. For example:")
    print()
    print("    export NRE_LDBWS_API_KEY=my-ldbws-api-key")
    print()
    print("To get a key, please see the NREWebServices documentation.")
    print()
    exit(1)

###################################################################################################
# init unicorn
unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(270)
unicorn.brightness(0.38)
width, height = unicorn.get_shape()

# create a list of colours we'll use to show the minutes until the next train
colours = [(0x26, 0xFF, 0x82),
           (0xFC, 0xFF, 0x71),
           (0xCC, 0x0A, 0x9C),
           (0x52, 0xA8, 0xF2),
           (0xF6, 0xF0, 0xD0),
           (0x26, 0xFF, 0x82),
           (0xFC, 0xFF, 0x71),
           (0xCC, 0x0A, 0x9C),
           (0x52, 0xA8, 0xF2),
           (0xF6, 0xF0, 0xD0),
           (0x26, 0xFF, 0x82),
           (0xFC, 0xFF, 0x71),
           (0xCC, 0x0A, 0x9C),
           (0x52, 0xA8, 0xF2),
           (0xF6, 0xF0, 0xD0)]

###################################################################################################

# instantiate LED matrix
# on the unicorn hat your options are: coordinates.straight(8) or coordinates.diagonal(8)
coords = coordinates.diagonal(8)

###################################################################################################
# Instantiate the web service session.
session = Session(API_URL, API_KEY)

prevFirstTrainIn = 0

while True:
    # get the time right now in minutes of the day
    timeNow = datetime.now(timezone('Europe/London'))
    timeNowInMin = timeNow.hour * 60 + timeNow.minute

    # try to get departure board, except URLerror (couldn't reach departure board API server)
    try:
        # Get a departure board containing the next 15 departures from headed for TO_STATION in resin.io.
        board = session.get_station_board(
            FROM_STATION,
            rows=15,
            include_departures=True,
            include_arrivals=False,
            to_filter_crs=TO_STATION,
            time_offset=3,
            time_window=120
        )

        minToNextTrains = []

        # Loop over all the train services in that board.
        # train departures are given as HH:MM strings
        # save minutes to next train to a list
        # if we are straddling midnight, add 24 hours to the train time
        for service in board.train_services:
            if service.etd == "On time":
                timeSplit = service.std.split(":")
                timeSplitHour = int(timeSplit[0])
                if timeNow.hour > 14 and timeSplitHour < 8:
                    timeSplitHour += 24
                minToThisTrain = timeSplitHour * 60 + int(timeSplit[1]) - timeNowInMin
                minToNextTrains.append(minToThisTrain)

            elif service.etd[2] == ":":
                timeSplit = service.etd.split(":")
                timeSplitHour = int(timeSplit[0])
                if timeNow.hour > 14 and timeSplitHour < 8:
                    timeSplitHour += 24
                minToThisTrain = timeSplitHour * 60 + int(timeSplit[1]) - timeNowInMin
                minToNextTrains.append(minToThisTrain)
            print("    {} to {}: due {}.".format(
                service.std,
                service.destination,
                service.etd
            ))

        # try to process train departure times, except not train departure times returned, pass
        try:
            # remove the minutes already counted from each train
            minToNextTrains.sort()
            shiftedMinsList = [minToNextTrains[0]]
            for i in range(len(minToNextTrains) - 1):
                shiftedMinsList.append(minToNextTrains[i + 1] - minToNextTrains[i])

            print(shiftedMinsList)

            # init values that help us keep track of which coordinates we should be using
            coordsLength = len(coords)
            tracker = 0

            # if a train has just left the station (or if this is our first run):
            # (of if the first train has become delayed)
            # cue animation
            if prevFirstTrainIn < shiftedMinsList[0]:
                for coord in reversed(coords):
                    x = coord[0]
                    y = coord[1]
                    r = 0
                    g = 0
                    b = 0
                    unicorn.set_pixel(x, y, r, g, b)
                    unicorn.show()
                    sleep(0.1)
                    tracker += 1
                    if tracker == coordsLength:
                        break
                tracker = 0
                for train in range(len(shiftedMinsList)):
                    for minute in range(shiftedMinsList[train]):
                        x = coords[tracker][0]
                        y = coords[tracker][1]
                        r = colours[train][0]
                        g = colours[train][1]
                        b = colours[train][2]
                        unicorn.set_pixel(x, y, r, g, b)
                        unicorn.show()
                        sleep(0.1)
                        tracker += 1
                        if tracker == coordsLength:
                            break
                    if tracker == coordsLength:
                        break

            # else: be boring
            else:
                for train in range(len(shiftedMinsList)):
                    for minute in range(shiftedMinsList[train]):
                        x = coords[tracker][0]
                        y = coords[tracker][1]
                        r = colours[train][0]
                        g = colours[train][1]
                        b = colours[train][2]
                        unicorn.set_pixel(x, y, r, g, b)
                        tracker += 1
                        if tracker == coordsLength:
                            break
                    if tracker == coordsLength:
                        break
                # if we don't have more trains, backfill LED's to black
                while tracker < coordsLength:
                    x = coords[tracker][0]
                    y = coords[tracker][1]
                    r = 0
                    g = 0
                    b = 0
                    unicorn.set_pixel(x, y, r, g, b)
                    tracker += 1
                unicorn.show()

            prevFirstTrainIn = shiftedMinsList[0]
        except IndexError:
            pass
    except URLError as e:
        print(e.reason)
    sleep(30)
