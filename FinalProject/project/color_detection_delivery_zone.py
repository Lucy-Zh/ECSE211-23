#!/usr/bin/python3
"""
This code handles the detection of the color from the values obtained from the color sensor.
This one is specifically for the detection of the delivery zones.
The general logic comes from the Hands on with BrickPi 2 Lecture slide.
Author: Nazia Chowdhury
"""
import math

# Average of the normalized values of RGB for each color.
# Data was collected by the Test Lead.
zoneRedR = 0.8009223042
zoneRedG = 0.123192429
zoneRedB = 0.07588526683
zoneGreenR = 0.2561182446
zoneGreenG = 0.5920031429
zoneGreenB = 0.1518786125
zoneOrangeR = 0.7850831432
zoneOrangeG = 0.1574974183
zoneOrangeB = 0.05741943848
zoneYellowR = 0.5371110826
zoneYellowG = 0.4002713468
zoneYellowB = 0.06261757062
zoneBlueR = 0.286503036
zoneBlueG = 0.3132329357
zoneBlueB = 0.4002640284
zonePurpleR = 0.7320625319
zonePurpleG = 0.1207037458
zonePurpleB = 0.1472337223


def get_delivery_zone_color(red, green, blue):

        # normalizing the values obtained by the color sensor
        nRed = red/(math.sqrt(red*red + green*green + blue*blue))
        nGreen = green/(math.sqrt(red*red + green*green + blue*blue))
        nBlue = blue/(math.sqrt(red*red + green*green + blue*blue))

        # calculating distance of the color from the Average of the normalized values of each delivery zone
        distBlue = math.sqrt((nRed - zoneBlueR) ** 2 + (nGreen - zoneBlueG) ** 2 + (nBlue - zoneBlueB) ** 2)
        distGreen = math.sqrt((nRed - zoneGreenR) ** 2 + (nGreen - zoneGreenG) ** 2 + (nBlue - zoneGreenB) ** 2)
        distYellow = math.sqrt((nRed - zoneYellowR) ** 2 + (nGreen - zoneYellowG) ** 2 + (nBlue - zoneYellowB) ** 2)
        distRed = math.sqrt((nRed - zoneRedR) ** 2 + (nGreen - zoneRedG) ** 2 + (nBlue - zoneRedB) ** 2)
        distOrange = math.sqrt((nRed - zoneOrangeR) ** 2 + (nGreen - zoneOrangeG) ** 2 + (nBlue - zoneOrangeB) ** 2)
        distPurple = math.sqrt((nRed - zonePurpleR) ** 2 + (nGreen - zonePurpleG) ** 2 + (nBlue - zonePurpleB) ** 2)

        color_zone_list = [distBlue, distGreen, distYellow, distRed, distOrange, distPurple]
        color_zone_list.sort() # the first array value determines which color is the closest to the value obtained from the color sensor

        if color_zone_list[0] == distBlue:
            #print("blue!")
            return "blue"
        if color_zone_list[0] == distGreen:
            #print("green!")
            return "green"
        if color_zone_list[0] == distYellow:
            #print("yellow!")
            return "yellow"
        if color_zone_list[0] == distRed:
            #print("red!")
            return "red"
        if color_zone_list[0] == distOrange:
            #print("orange!")
            return "orange"
        if color_zone_list[0] == distPurple:
            #print("purple!")
            return "purple"
