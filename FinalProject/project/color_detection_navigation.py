#!/usr/bin/python3
"""
This code handles the detection of the color from the values obtained from the color sensor.
This one is specifically for the detection of the routes.
The general logic comes from the Hands on with BrickPi 2 Lecture slide.
Author: Nazia Chowdhury
"""

from utils.brick import EV3ColorSensor, wait_ready_sensors, BP
import time
import math

COLOR_SENSOR_1 = EV3ColorSensor(1)

# Average of the normalized values of RGB for each color.
# Data was collected by the Test Lead.
zoneRedR = 0.7865179088
zoneRedG = 0.1591043755
zoneRedB = 0.05437771574
zoneGreenR = 0.2195924222
zoneGreenG = 0.6843564171
zoneGreenB = 0.09605116068
zoneBlueR = 0.2656504182
zoneBlueG = 0.4049780494
zoneBlueB = 0.3293715324
zoneWhiteR = 0.4414476473
zoneWhiteG = 0.3817272739
zoneWhiteB = 0.1768250788

def navigation():
    wait_ready_sensors()
    try:
        while True:
            time.sleep(1)
            red, green, blue, trp = COLOR_SENSOR_1.get_value() # getting each R,G,B color

            # normalizing the values obtained by the color sensor
            nRed = red/(math.sqrt(red*red + green*green + blue*blue))
            nGreen = green/(math.sqrt(red*red + green*green + blue*blue))
            nBlue = blue/(math.sqrt(red*red + green*green + blue*blue))

            # calculating distance of the color from the Average of the normalized values of each delivery zone
            distBlue = math.sqrt((nRed - zoneBlueR) ** 2 + (nGreen - zoneBlueG) ** 2 + (nBlue - zoneBlueB) ** 2)
            distGreen = math.sqrt((nRed - zoneGreenR) ** 2 + (nGreen - zoneGreenG) ** 2 + (nBlue - zoneGreenB) ** 2)
            distRed = math.sqrt((nRed - zoneRedR) ** 2 + (nGreen - zoneRedG) ** 2 + (nBlue - zoneRedB) ** 2)
            distWhite = math.sqrt((nRed - zoneWhiteR) ** 2 + (nGreen - zoneWhiteG) ** 2 + (nBlue - zoneWhiteB) ** 2)

            color_zone_list = [distBlue, distGreen, distRed, distWhite]
            color_zone_list.sort() # the first array value determines which color is the closest to the value obtained from the color sensor

            if color_zone_list[0] == distWhite:
                print("white!")
            if color_zone_list[0] == distBlue:
                print("blue!")
            if color_zone_list[0] == distRed:
                print("red!")
            if color_zone_list[0] == distGreen:
                print("green!")

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

if __name__ == "__main__":
    navigation()
