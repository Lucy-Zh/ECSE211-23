#!/usr/bin/python3
"""
This code handles the delivery system.
Author: Yu An Lu, Nazia Chowdhury, Lucy Zhang, and Samantha Perez Hoffman
"""

from utils.brick import EV3ColorSensor, wait_ready_sensors, BP, Motor, TouchSensor
import time
import color_detection_navigation as cdn
import color_detection_delivery_zone as cddz
#import threading

COLOR_SENSOR_1 = EV3ColorSensor(3)
COLOR_SENSOR_2 = EV3ColorSensor(1)
TOUCH_SENSOR =TouchSensor(2)
LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("B")
PUSH_MOTOR = Motor("A")
CONVEYOR_BELT_MOTOR = Motor("D")

POWER_LIMIT = 80       # Power limit = 80%
SPEED_LIMIT = 720      # Speed limit = 720 deg per sec (dps)

## Touch Button Activation/Deactivation Code

# on/off button boolean
stop_system = True

def system_start():
    while stop_system:
        if TOUCH_SENSOR.is_pressed():
            print("System Activated!")
            stop_system = False
    print ("Navigation Time!")
    navigation()

## Path Navigation Code

# green line count
delivery_count = 0
# return loading bay boolean
return_loading_bay = False

def motor_set_up():
    print("Motor Set up")
    
    # Encoder keeps a record of degrees turned
    LEFT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    RIGHT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)

def turn_right():
    LEFT_MOTOR.set_dps(150) # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(90) # Rotate the left motor only to turn right
    RIGHT_MOTOR.set_position_relative(0)
    time.sleep(1)

def turn_left():
    print("left!")
    LEFT_MOTOR.set_dps(150) # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(0) # Rotate the right motor only to turn left
    RIGHT_MOTOR.set_position_relative(90)
    time.sleep(1)

def move_forward():
    print("straight!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(90)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(90)
    time.sleep(1)

def stop_moving():
    print("stop!")
    global delivery_count
    BP.reset_all()
    # call the delivery drop-off mechanism
    read_input_drop_off()
    delivery_count += 1
    # move away from green line
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(180)
    time.sleep(1)

def turn_180():
    print("Turning 180 degrees!")
    LEFT_MOTOR.set_dps(90)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(90)
    LEFT_MOTOR.set_position_relative(0)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(360)
    time.sleep(1)

def navigation():
    global return_loading_bay, stop_system, delivery_count
    wait_ready_sensors()
    try:
        while True:
            # check if all deliveries have been made
            if delivery_count == 6:
                return_loading_bay = True
                turn_180()

            time.sleep(1)
            red, green, blue, trp = COLOR_SENSOR_1.get_value() # getting each R,G,B color
            color = cdn.get_navigation_color(red, green, blue) # getting the color from color detection navigation

            if color == "white":
                #print("white!")
                move_forward()
            if color == "blue":
                #print("blue!")
                if not return_loading_bay:
                    turn_right()
                else:
                    turn_left()
            if color == "red":
                #print("red!")
                if not return_loading_bay:
                    turn_left()
                else:
                    turn_right()
            if color == "green" and not return_loading_bay:
                #print("green!")
                stop_moving()
            if color == "yellow" and return_loading_bay:
                #print("yellow!")
                stop_system = True
                turn_180()
                system_start()


    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

## Drop-off Mechanism Code

#color detected by the color sensor 
detectedColor = -1
currentPosition = 2 #0 to 5 - starts at yellow 
rotationPerPositionConstant = -115
# position of cubes: 0 = red, 1 = orange, 2 = yellow, 3 = green, 4 = blue, 5 = pink

def read_input_drop_off():
    global detectedColor
    wait_ready_sensors()
    try:
        while True:
            print("in while true read_input_drop_off")
            time.sleep(3)
            red, green, blue, trp = COLOR_SENSOR_2.get_value() # getting each R,G,B color
            color = cddz.get_delivery_zone_color(red, green, blue) # getting the color from color detection delivery zone

            if color == "blue":
                #print("blue!")
                detectedColor = 4
                moveConveyorBelt()
            if color == "green":
                #print("green!")
                detectedColor = 3
                moveConveyorBelt()
            if color == "yellow":
                #print("yellow!")
                detectedColor = 2
                moveConveyorBelt()
            if color == "red":
                #print("red")
                detectedColor = 0
                moveConveyorBelt()
            if color == "orange":
                #print("orange!")
                detectedColor = 1
                moveConveyorBelt()
            if color == "purple":
                #print("purple!")
                detectedColor = 5
                moveConveyorBelt()
            time.sleep(3)

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        CONVEYOR_BELT_MOTOR.set_position_relative(0)
        PUSH_MOTOR.set_position_relative(0)
        BP.reset_all()

def moveConveyorBelt():
    #print("moveConveyorBelt entered")
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
    #print("push cube")
    # Encoder keeps a record of degrees turned
    #PUSH_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    #PUSH_MOTOR.set_dps(SPEED)                              # Set the speed for the motor
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED)
    PUSH_MOTOR.set_position_relative(-50) # Rotate negative rotation when pushing out cube 
    time.sleep(2)
    PUSH_MOTOR.set_position_relative(50) # Rotate back to original position
    time.sleep(2)


if __name__ == "__main__":
    motor_set_up()
    system_start()

