#!/usr/bin/env python3

"""
Module to do all the Marching Band actions. 
This file must be run on the robot.
"""

from utils.brick import TouchSensor, wait_ready_sensors
from utils.brick import Motor

motor = Motor("A")

TOUCH_SENSOR_1 = TouchSensor(1)
TOUCH_SENSOR_2 = TouchSensor(2)
TOUCH_SENSOR_3 = TouchSensor(3)
TOUCH_SENSOR_4 = TouchSensor(4)

isMotorOn = False


wait_ready_sensors()  # Note: Touch sensors actually have no initialization time

def emergency_stop():
    motor.set_power(0) 

def start_motor(): 
    motor.set_power(100)
    motor.set_position_relative(90)
    motor.set_position_relative(-90)
    isMotorOn = True

def stop_motor():
    motor.set_dps(0)
    isMotorOn = False

def button_press():
    "In an infinite loop, if the touch sensor is pressed ..."
    try:
        while True:
            if isMotorOn == True:
                start_motor()


            if TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and TOUCH_SENSOR_3.is_pressed() and TOUCH_SENSOR_4.is_pressed():
                emergency_stop()
            elif TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and isMotorOn == False:
                start_motor()
            elif TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and isMotorOn == True:
                stop_motor()
            

    # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    except BaseException:
        exit()


if __name__ == '__main__':

    # TODO Implement this function
    button_press()
