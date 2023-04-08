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
zoneRedR = 0.8095180982
zoneRedG = 0.12036282
zoneRedB = 0.07011908174
zoneGreenR = 0.2561182446
zoneGreenG = 0.5920031429
zoneGreenB = 0.1518786125
zoneOrangeR = 0.7319939999
zoneOrangeG = 0.2033230213
zoneOrangeB = 0.06468297882
zoneYellowR = 0.5092062061
zoneYellowG = 0.4287423951
zoneYellowB = 0.060513989
zoneBlueR = 0.286503036
zoneBlueG = 0.3132329357
zoneBlueB = 0.4002640284
zonePurpleR = 0.7006285831
zonePurpleG = 0.136832503
zonePurpleB = 0.1625081666
zoneWhiteR = 0.3814265938
zoneWhiteG = 0.3587578197
zoneWhiteB = 0.2598155864


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
        distWhite = math.sqrt((nRed - zoneWhiteR) ** 2 + (nGreen - zoneWhiteG) ** 2 + (nBlue - zoneWhiteB) ** 2)

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
            if blue >= 100:
                return "white"
            else:
                return "yellow"
#             return "yellow"
        if color_zone_list[0] == distRed:
            if red >= 200:
#                 if green >= 90:
#                     return "orange"
#                 else:
                return "red"
            else:
                return "purple"
            #print("red!")
#              return "red"
        if color_zone_list[0] == distOrange:
            #print("orange!")
            return "orange"
        if color_zone_list[0] == distPurple:
            if red >= 200:
                return "red"
            else:
                return "purple"
#              return "purple"
        if color_zone_list[0] == distWhite:
            if blue >= 100:
                return "white"
            else:
                return "yellow"
#             #print("white!")
#             return "white"
        