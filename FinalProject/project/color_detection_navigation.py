#!/usr/bin/python3
"""
This code handles the detection of the color from the values obtained from the color sensor.
This one is specifically for the detection of the routes.
The general logic comes from the Hands on with BrickPi 2 Lecture slide.
Author: Nazia Chowdhury
"""
import math

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
zoneYellowR = 0.5371110826
zoneYellowG = 0.4002713468
zoneYellowB = 0.06261757062

def get_navigation_color(red, green, blue):
    # normalizing the values obtained by the color sensor
    nRed = red/(math.sqrt(red*red + green*green + blue*blue))
    nGreen = green/(math.sqrt(red*red + green*green + blue*blue))
    nBlue = blue/(math.sqrt(red*red + green*green + blue*blue))

    # calculating distance of the color from the Average of the normalized values of each delivery zone
    distBlue = math.sqrt((nRed - zoneBlueR) ** 2 + (nGreen - zoneBlueG) ** 2 + (nBlue - zoneBlueB) ** 2)
    distGreen = math.sqrt((nRed - zoneGreenR) ** 2 + (nGreen - zoneGreenG) ** 2 + (nBlue - zoneGreenB) ** 2)
    distRed = math.sqrt((nRed - zoneRedR) ** 2 + (nGreen - zoneRedG) ** 2 + (nBlue - zoneRedB) ** 2)
    distWhite = math.sqrt((nRed - zoneWhiteR) ** 2 + (nGreen - zoneWhiteG) ** 2 + (nBlue - zoneWhiteB) ** 2)
    distYellow = math.sqrt((nRed - zoneYellowR) ** 2 + (nGreen - zoneYellowG) ** 2 + (nBlue - zoneYellowB) ** 2)

    color_zone_list = [distBlue, distGreen, distRed, distWhite, distYellow]
    color_zone_list.sort() # the first array value determines which color is the closest to the value obtained from the color sensor

    if color_zone_list[0] == distWhite:
        #print("white!")
        return "white"
    if color_zone_list[0] == distBlue:
        #print("blue!")
        return "blue"
    if color_zone_list[0] == distRed:
        #print("red!")
        return "red"
    if color_zone_list[0] == distGreen:
        #print("green!")
        return "green"
    if color_zone_list[0] == distYellow:
        #print("yellow!")
        if blue >= 40:
            return "white"
        else:
            return "yellow"
        #return "yellow"
