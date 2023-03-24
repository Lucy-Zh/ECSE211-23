#!/usr/bin/python3
"""
This code handles the delivery of the cubes.
Author: Lucy Zhang, and Samantha Perez Hoffman
The color detection algorithm from color_detection_delivery_zone.py is used.
"""
# Detect color of delivery zone 
# Move conveyor belt so that detected colored cube is at the right position to push
# Push cube into delivery zone

from utils.brick import EV3ColorSensor, wait_ready_sensors, BP, Motor
import time
import math

COLOR_SENSOR_2 = EV3ColorSensor(1)
CONVEYOR_BELT_MOTOR = Motor("B") # Motor used for convoyor belt
PUSH_MOTOR = Motor("A") # Motor used for test

POWER_LIMIT = 80       # Power limit = 80%
SPEED_LIMIT = 720      # Speed limit = 720 deg per sec (dps)

SPEED = 50

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

#color detected by the color sensor 
detectedColor = -1
currentPosition = 2 #0 to 5 - starts at yellow 
rotationPerPositionConstant = -115
pushingRotationConstant = -75
# position of cubes: 0 = red, 1 = orange, 2 = yellow, 3 = green, 4 = blue, 5 = pink

wait_ready_sensors()
def read_input_drop_off():
    global detectedColor, zoneRedR, zoneRedG, zoneRedB, zoneGreenR, zoneGreenG, zoneGreenB, zoneOrangeR, zoneOrangeG, zoneOrangeB, zoneYellowR, zoneYellowG, zoneYellowB, zoneBlueR, zoneBlueG, zoneBlueB, zonePurpleR, zonePurpleG, zonePurpleB    
    try:
        while True:
            print("in while true read_input_drop_off")
            time.sleep(3)
            red, green, blue, trp = COLOR_SENSOR_2.get_value() # getting each R,G,B color

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
                print("blue!") # temp logic until we implement the rest
                detectedColor = 4
                moveConveyorBelt()
            if color_zone_list[0] == distGreen:
                print("green!")
                detectedColor = 3
                moveConveyorBelt()
            if color_zone_list[0] == distYellow:
                print("yellow!")
                detectedColor = 2
                moveConveyorBelt()
            if color_zone_list[0] == distRed:
                print("red")
                detectedColor = 0
                moveConveyorBelt()
            if color_zone_list[0] == distOrange:
                print("orange!")
                detectedColor = 1
                moveConveyorBelt()
            if color_zone_list[0] == distPurple:
                print("purple!")
                detectedColor = 5
                moveConveyorBelt()
            time.sleep(3)
    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        CONVEYOR_BELT_MOTOR.set_position_relative(0)
        PUSH_MOTOR.set_position_relative(0)
        BP.reset_all()

def moveConveyorBelt():
    print("moveConveyorBelt entered")
    global detectedColor, currentPosition, rotationPerPositionConstant
    # move the conveyor belt so that the detected color is at the right position to push
    # this is where the logic for the conveyor belt will go

    # TODO - find rotation required to move conveyer belt 1 position 
    # calculate the number of positions required to move 
    numberOfPositions = currentPosition - detectedColor
    # calculate the number of rotations required to move the conveyer belt
    rotations = numberOfPositions * rotationPerPositionConstant

    # Encoder keeps a record of degrees turned
    #CONVEYOR_BELT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    #CONVEYOR_BELT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits                             # Set the speed for the motor
    #CONVEYOR_BELT_MOTOR.set_dps(SPEED)
    #CONVEYOR_BELT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
    CONVEYOR_BELT_MOTOR.set_position_relative(rotations)             # Rotate the desired amount of degrees
    
    time.sleep(5)
    #CONVEYOR_BELT_MOTOR.set_power(0)
    pushCube() # push cube into delivery zone

    # update currentPosition 
    currentPosition = detectedColor

def pushCube():
    # push cube into delivery zone
    # this is where the logic for the pusher will go
    print("push cube")
    # Encoder keeps a record of degrees turned
    #PUSH_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    #PUSH_MOTOR.set_dps(SPEED)                              # Set the speed for the motor
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED)
    PUSH_MOTOR.set_position_relative(-50) # Rotate negative rotation when pushing out cube 
    time.sleep(2)
    PUSH_MOTOR.set_position_relative(50) # Rotate back to original position
    time.sleep(2)

if __name__ == '__main__':
   CONVEYOR_BELT_MOTOR.set_position_relative(0)
   PUSH_MOTOR.set_position_relative(0)
   #CONVEYOR_BELT_MOTOR.set_power(0)
   read_input_drop_off()

        
