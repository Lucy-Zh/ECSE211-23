#!/usr/bin/python3
"""
This code handles the detection of the color from the values obtained from the color sensor.
This one is specifically for the navigation path subsystem.
The general logic comes from the Hands on with BrickPi 2 Lecture slide.
Author: Nazia Chowdhury
"""

from utils.brick import EV3ColorSensor, wait_ready_sensors, BP, Motor
import time
import math

COLOR_SENSOR_1 = EV3ColorSensor(1)
TOUCH_SENSOR = EV3ColorSensor(2)
LEFT_MOTOR = Motor("C") # Auxilliary Motor used for test
RIGHT_MOTOR = Motor("B")    # Right motor in Port D

POWER_LIMIT = 80       # Power limit = 80%
SPEED_LIMIT = 720      # Speed limit = 720 deg per sec (dps)

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

# green line count
delivery_count = 0
# return loading bay boolean
return_loading_bay = False
# on/off button boolean
stop_system = True

def motor_set_up():
    print("Motor Set up")
    
    # Encoder keeps a record of degrees turned
    LEFT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    RIGHT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)
    LEFT_MOTOR.set_dps(50)
    RIGHT_MOTOR.set_dps(50)

def turn_right():
    #LEFT_MOTOR.set_dps(speed_left)                              # Set the speed for the motor
    #LEFT_MOTOR.set_limits(POWER_LIMIT, speed_left)
    LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
    #RIGHT_MOTOR.set_dps(speed_right)                              # Set the speed for the motor
    #RIGHT_MOTOR.set_limits(POWER_LIMIT, speed_right)
    RIGHT_MOTOR.set_position_relative(90) 

def turn_left():
    #LEFT_MOTOR.set_dps(speed_left)                              # Set the speed for the motor
    #LEFT_MOTOR.set_limits(POWER_LIMIT, speed_left)
    LEFT_MOTOR.set_position_relative(90)             # Rotate the desired amount of degrees
    #RIGHT_MOTOR.set_dps(speed_right)                              # Set the speed for the motor
    #RIGHT_MOTOR.set_limits(POWER_LIMIT, speed_right)
    RIGHT_MOTOR.set_position_relative(180)

def move_forward():
    #LEFT_MOTOR.set_dps(speed_left)                              # Set the speed for the motor
    #LEFT_MOTOR.set_limits(POWER_LIMIT, speed_left)
    LEFT_MOTOR.set_position_relative(90)             # Rotate the desired amount of degrees
    #RIGHT_MOTOR.set_dps(speed_right)                              # Set the speed for the motor
    #RIGHT_MOTOR.set_limits(POWER_LIMIT, speed_right)
    RIGHT_MOTOR.set_position_relative(90)

def stop_moving():
        BP.reset_all()
        delivery_count += 1
        # call the delivery drop-off mechanism
        motor_set_up()
        navigation()
        
def navigation():

    wait_ready_sensors()
    try:
        while True:
            red, green, blue = COLOR_SENSOR_1.get_value() # getting each R,G,B color

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
                #print("white!")
                move_forward()
            if color_zone_list[0] == distBlue:
                #print("blue!") # temp logic until we implement the rest
                if not return_loading_bay:
                    turn_left()
                else:
                    turn_right()
            if color_zone_list[0] == distRed:
                #print("red!")
                if not return_loading_bay:
                    turn_right()
                else:
                    turn_left()
            if color_zone_list[0] == distGreen:
                #print("green!")
                stop_moving()

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

if __name__ == "__main__":
    motor_set_up()
    navigation()
