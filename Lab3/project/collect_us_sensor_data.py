#!/usr/bin/env python3

"""
This test is used to collect data from the ultrasonic sensor.
It must be run on the robot.
"""

from utils import sound
from utils.brick import TouchSensor, EV3UltrasonicSensor, wait_ready_sensors, reset_brick
from time import sleep


DELAY_SEC = 0.01  # seconds of delay between measurements
US_SENSOR_DATA_FILE = "../data_analysis/us_sensor.csv"
SOUND = sound.Sound(duration=0.3, pitch="A4", volume=60)

print("Program start.\nWaiting for sensors to turn on...")

TOUCH_SENSOR = TouchSensor(1)
US_SENSOR = EV3UltrasonicSensor(2)


wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.
print("Done waiting.")


def collect_continuous_us_data():
    "Collect continuous data from the ultrasonic sensor between two button presses."
    try:
        output_file = open(US_SENSOR_DATA_FILE, "w")
        while not TOUCH_SENSOR.is_pressed():
            pass  # do nothing while waiting for first button press
        print("Touch sensor pressed")
        sleep(1)
        print("Starting to collect US distance samples")
        while not TOUCH_SENSOR.is_pressed():
            us_data = US_SENSOR.get_value()  # Float value in centimeters 0, capped to 255 cm
            if us_data is not None: # If None is given, then data collection failed that time
                print(us_data)
                output_file.write(f"{us_data}\n")
            sleep(DELAY_SEC)
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        pass
    finally:
        print("Done collecting US distance samples")
        output_file.close()
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()

if __name__ == "__main__":
    collect_continuous_us_data()
