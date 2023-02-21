#!/usr/bin/env python3

"""
Module to do all the Marching Band actions. 
This file must be run on the robot.
"""
from utils import sound
from utils.brick import TouchSensor, wait_ready_sensors
from utils.brick import Motor

motor = Motor("A")

SOUND_1 = sound.Sound(duration=0.3, pitch="C4", volume=120)
SOUND_2 = sound.Sound(duration=0.3, pitch="G4", volume=120)
SOUND_3 = sound.Sound(duration=0.3, pitch="A4", volume=120)
SOUND_4 = sound.Sound(duration=0.3, pitch="E4", volume=120)

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
            if isMotorOn == True:
                start_motor()


            if TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and TOUCH_SENSOR_3.is_pressed() and TOUCH_SENSOR_4.is_pressed():
                emergency_stop()
            elif TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and isMotorOn == False:
                start_motor()
            elif TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and isMotorOn == True:
                stop_motor()
            elif TOUCH_SENSOR_1.is_pressed():
                play_sound_1()
            elif TOUCH_SENSOR_2.is_pressed():
                play_sound_2()
            elif TOUCH_SENSOR_3.is_pressed():
                play_sound_3()
            elif TOUCH_SENSOR_4.is_pressed():
                play_sound_4()
            

    # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    except BaseException:
        exit()


if __name__ == '__main__':

    # TODO Implement this function
    button_press()
