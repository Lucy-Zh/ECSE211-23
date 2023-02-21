#!/usr/bin/env python3

"""
Module to do all the Marching Band actions. 
This file must be run on the robot.
"""
from utils import sound
from utils.brick import TouchSensor, wait_ready_sensors
from utils.brick import Motor
import time

motor = Motor("A")

SOUND_1 = sound.Sound(duration=0.3, pitch="C4", volume=120)
SOUND_2 = sound.Sound(duration=0.3, pitch="G4", volume=120)
SOUND_3 = sound.Sound(duration=0.3, pitch="A4", volume=120)
SOUND_4 = sound.Sound(duration=0.3, pitch="E4", volume=120)

TOUCH_SENSOR_1 = TouchSensor(1)
TOUCH_SENSOR_2 = TouchSensor(2)
TOUCH_SENSOR_3 = TouchSensor(3)
TOUCH_SENSOR_4 = TouchSensor(4)

is_ts1_pressed = False
is_ts2_pressed = False
is_ts3_pressed = False
is_ts4_pressed = False
isMotorOn = False


wait_ready_sensors()  # Note: Touch sensors actually have no initialization time
def read_input():
    t_end = time.time() + 5
    while True:
        if TOUCH_SENSOR_1.is_pressed() or TOUCH_SENSOR_2.is_pressed() or TOUCH_SENSOR_3.is_pressed() or TOUCH_SENSOR_4.is_pressed():
            break

    while time.time() < t_end:
        if TOUCH_SENSOR_1.is_pressed():
            is_ts1_pressed = True
        if TOUCH_SENSOR_2.is_pressed():
            is_ts2_pressed = True
        if TOUCH_SENSOR_3.is_pressed():
            is_ts3_pressed = True
        if TOUCH_SENSOR_4.is_pressed():
            is_ts4_pressed = True

def reset_input():
    is_ts1_pressed = False
    is_ts2_pressed = False
    is_ts3_pressed = False
    is_ts4_pressed = False

def emergency_stop():
    exit()

def start_motor(): 
    motor.set_power(50)
    motor.set_position_relative(50)
    motor.set_position_relative(-50)
    isMotorOn = True

def stop_motor():
    motor.set_dps(0)
    isMotorOn = False

def play_sound_1():
    "Play a single note."
    SOUND_1.play()
    SOUND_1.wait_done()

def play_sound_2():
    "Play a single note."
    SOUND_2.play()
    SOUND_2.wait_done()

def play_sound_3():
    "Play a single note."
    SOUND_3.play()
    SOUND_3.wait_done()

def play_sound_4():
    "Play a single note."
    SOUND_4.play()
    SOUND_4.wait_done()

def button_press():
    "In an infinite loop, if the touch sensor is pressed ..."
    try:
        while True:
            read_input()

            if isMotorOn == True:
                start_motor()

            if is_ts1_pressed and is_ts2_pressed and is_ts3_pressed and is_ts4_pressed:
                emergency_stop()
            elif is_ts1_pressed and is_ts2_pressed and isMotorOn == False:
                start_motor()
            elif is_ts1_pressed and is_ts2_pressed and isMotorOn == True:
                stop_motor()
            elif is_ts1_pressed:
                play_sound_1()
            elif is_ts2_pressed:
                play_sound_2()
            elif is_ts3_pressed:
                play_sound_3()
            elif is_ts4_pressed:
                play_sound_4()

            reset_input()
            

    # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    except BaseException:
        exit()


if __name__ == '__main__':

    # TODO Implement this function
    button_press()
