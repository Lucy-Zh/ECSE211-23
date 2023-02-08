#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
from utils.brick import EV3ColorSensor, wait_ready_sensors, TouchSensor, reset_brick
from time import sleep


COLOR_SENSOR_DATA_FILE = "/home/pi/ecse211/lab2-starter-code_w23/data_analysis/color_sensor.csv"
DELAY_SEC = 0.01  # seconds of delay between measurement

# complete this based on your hardware setup
COLOR_SENSOR = EV3ColorSensor(2)
TOUCH_SENSOR = TouchSensor(1)
TOUCH_SENSOR_STOP = TouchSensor(3)

# Input True to see what the robot is trying to initialize! False to be silent.
wait_ready_sensors(True)


def collect_color_sensor_data():
    "Collect color sensor data."
    output_file = open(COLOR_SENSOR_DATA_FILE, "w")
    try:
        while True:
            cs_data = COLOR_SENSOR.get_value()
            if TOUCH_SENSOR.is_pressed():
                print(f"{cs_data}")
                output_file.write(f"{cs_data}\n")
                while TOUCH_SENSOR.is_pressed():
                    pass
            if TOUCH_SENSOR_STOP.is_pressed():
                output_file.close()
                reset_brick()
                exit()

            sleep(DELAY_SEC)
    except BaseException:
        pass


if __name__ == "__main__":
    collect_color_sensor_data()
