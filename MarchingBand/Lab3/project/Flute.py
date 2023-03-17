#!/usr/bin/env python3

"""
Module to play sounds when the touch sensor is pressed.
This file must be run on the robot.
"""

from utils import sound
from utils.brick import TouchSensor, wait_ready_sensors

SOUND_1 = sound.Sound(duration=0.3, pitch="C4", volume=120)
SOUND_2 = sound.Sound(duration=0.3, pitch="G4", volume=120)
SOUND_3 = sound.Sound(duration=0.3, pitch="A4", volume=120)
SOUND_4 = sound.Sound(duration=0.3, pitch="E4", volume=120)
TOUCH_SENSOR_1 = TouchSensor(1)
TOUCH_SENSOR_2 = TouchSensor(2)
TOUCH_SENSOR_3 = TouchSensor(3)
TOUCH_SENSOR_4 = TouchSensor(4)


wait_ready_sensors()  # Note: Touch sensors actually have no initialization time


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


def play_sound_on_button_press():
    "In an infinite loop, play a single note when the touch sensor is pressed."
    try:
        while True:
            if TOUCH_SENSOR_1.is_pressed():
                play_sound_1()

            if TOUCH_SENSOR_2.is_pressed():
                play_sound_2()

            if TOUCH_SENSOR_3.is_pressed():
                play_sound_3()

            if TOUCH_SENSOR_4.is_pressed():
                play_sound_4()

            if TOUCH_SENSOR_1.is_pressed() and TOUCH_SENSOR_2.is_pressed() and TOUCH_SENSOR_3.is_pressed() and TOUCH_SENSOR_4.is_pressed():
                exit()
    # capture all exceptions including KeyboardInterrupt (Ctrl-C)
    except BaseException:
        exit()


if __name__ == '__main__':

    play_sound_on_button_press()