#!/usr/bin/python3
"""DPM Hands On Example 3 (Lecture 9) - MotorDemo

A simple interactive program that allows the user to specify the rotation and 
speed for an EV3 Large Motor. Prgoram operates a loop until ^C entered.

Author: F.P. Ferrie, Ryan Au
Date: January 13th, 2022
"""

from utils.brick import BP, Motor
import time

PUSH_MOTOR = Motor("C") # Auxilliary Motor used for test

POWER_LIMIT = 80       # Power limit = 80%
SPEED_LIMIT = 720      # Speed limit = 720 deg per sec (dps)

try:
    print("Motor Position Control Demo")

    # Encoder keeps a record of degrees turned
    PUSH_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    
    #CONVEYOR_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)

    while True:
        try:
            speed = int(input('Enter speed left (enter empty input to quit):'))           # Get the speed from user input
            rotation = int(input('Enter rotation change in degrees (+/- degrees):')) # Get the degrees to rotate from user input 
        except ValueError:
            print("Non-integer value inputted. Closing Program.")     # Input any non-integer to quit program
            BP.reset_all()
            exit()
        try:
            PUSH_MOTOR.set_dps(speed)                              # Set the speed for the motor
            PUSH_MOTOR.set_limits(POWER_LIMIT, speed)
            PUSH_MOTOR.set_position_relative(rotation)             # Rotate the desired amount of degrees
        except IOError as error:
            print(error)

except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
    BP.reset_all()

