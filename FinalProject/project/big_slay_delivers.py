#!/usr/bin/python3
"""
This code handles the delivery system.
Author: Yu An Lu, Nazia Chowdhury, Lucy Zhang, and Samantha Perez Hoffman
"""

from utils.brick import EV3ColorSensor, wait_ready_sensors, BP, Motor, TouchSensor
import time
import color_detection_navigation as cdn
import color_detection_delivery_zone as cddz
import threading
import operator

COLOR_SENSOR_1 = EV3ColorSensor(3)
COLOR_SENSOR_2 = EV3ColorSensor(4)
TOUCH_SENSOR =TouchSensor(1)
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
    global stop_system
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
#array of pushed blocks
#position of cubes: 0 = red, 1 = orange, 2 = yellow, 3 = green, 4 = blue, 5 = pink
block_pushed = [False, False, False, False, False, False]

# delivery navigation booleans
zone_navigation = False
zone_color_detected = False
zone_white_detected = False
zone_color = ""
sleep_time = 0.2
num = 3

def motor_set_up():
    print("Motor Set up")
    
    # Encoder keeps a record of degrees turned
    LEFT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    RIGHT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    LEFT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    RIGHT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)
    PUSH_MOTOR.set_power(0)
    CONVEYOR_BELT_MOTOR.set_power(0)

def turn_right():
    LEFT_MOTOR.set_dps(150) # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(85) # Rotate the left motor only to turn right
    RIGHT_MOTOR.set_position_relative(0)
    time.sleep(0.5)

def turn_left():
    print("left!")
    LEFT_MOTOR.set_dps(150) # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(0) # Rotate the right motor only to turn left
    RIGHT_MOTOR.set_position_relative(85)
    time.sleep(0.5)

def move_forward():
    print("straight!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(90)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(90)
    time.sleep(0.5)
    
def move_forward_small():
    global sleep_time, num
    print("move_forward_small!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(15*num)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(0)
    time.sleep(sleep_time)
    
def move_forward_small_zone():
    global sleep_time, num
    print("move_forward_small_zone!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(10*num)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(10*num)
    time.sleep(sleep_time)

def move_left_red():
    global sleep_time, num
    print("move_forward_red!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(0)
    RIGHT_MOTOR.set_position_relative(10*num)
    time.sleep(sleep_time)

def turn_right_white():
    global sleep_time, num
    print("turn_right_white!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(10*num)
    RIGHT_MOTOR.set_position_relative(0)
    time.sleep(sleep_time)

def turn_left_white():
    global sleep_time, num
    print("turn_left_white!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(0)
    RIGHT_MOTOR.set_position_relative(10*num)
    time.sleep(sleep_time)

def stop_moving():
    global zone_color, zone_color_detected, delivery_count, sleep_time, num, zone_white_detected
    print("stop!")
#     LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
#     RIGHT_MOTOR.set_dps(150)
#     LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
#     RIGHT_MOTOR.set_position_relative(180)
    # get delivery zone color
#     move_forward()
#     print("first move forward")
    # call the delivery drop-off mechanism
    read_input_drop_off(zone_color)
    # move straight forward from green line
#     LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
#     RIGHT_MOTOR.set_dps(150)
#     LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
#     RIGHT_MOTOR.set_position_relative(180)
    delivery_count += 1
    zone_white_detected = False
    sleep_time = 0.2
    num = 3
    time.sleep(0.3)
    
def zone_color_detection():
    global delivery_color_index, zone_navigation, zone_color_detected, zone_color, zone_white_detected
    wait_ready_sensors()
    try:
        while True:
            #print("navigation while True drop off")
            if zone_navigation:
                color_dict = { "blue": 0, "green": 0, "yellow": 0, "red": 0, "orange": 0, "purple": 0, "white": 0}
                for x in range(10):
                    red, green, blue, trp = COLOR_SENSOR_2.get_value()
                    _color = cddz.get_delivery_zone_color(red, green, blue)
                    value = color_dict.get(_color)
                    value = value + 1
                    color_dict.update({_color: value})
                # sort the 10 detected colors
                sorted_color_list = sorted(color_dict.items(), key=lambda kv: kv[1])
                color =  sorted_color_list[6][0]
                if not zone_color_detected and color != "white":
                    print("potential drop off zone detected")
                    print(sorted_color_list)
                    print(color)
                    #if block_pushed[delivery_color_index] == True:
                        #print("already pushed")
                    #else:
                    print([red,green,blue])
                    print("new color zone detected")
                    zone_color = color
                    zone_color_detected = True
                if zone_color_detected and color == "white":
                    zone_white_detected = True
                    zone_color_detected = False
                    zone_navigation = False
                time.sleep(0.2)

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

def turn_180():
    print("Turning 180 degrees!")
    LEFT_MOTOR.set_dps(90)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(90)
    LEFT_MOTOR.set_position_relative(1440)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(0)
    time.sleep(15)

def navigation():
    global return_loading_bay, stop_system, delivery_count, zone_navigation, zone_color_detected, sleep_time, zone_white_detected
    wait_ready_sensors()
    try:
        while True:
            print("navigation while True")
            # check if all deliveries have been made
            if delivery_count == 6:
                return_loading_bay = True
                turn_180()
                delivery_count = 0

            #time.sleep(1)
            color_dict = { "blue": 0, "green": 0, "yellow": 0, "red": 0, "white": 0}
            for x in range(10):
                red, green, blue, trp = COLOR_SENSOR_1.get_value()
                _color = cdn.get_navigation_color(red, green, blue)
                value = color_dict.get(_color)
                value = value + 1
                color_dict.update({_color: value})
            # sort the 10 detected colors
            sorted_color_list = sorted(color_dict.items(), key=lambda kv: kv[1])
            color =  sorted_color_list[4][0]
            # if delivery color is detected
            if zone_white_detected:
                print("zone white detected!")
                stop_moving()
            #elif color == "white" and not zone_navigation:
                #print("white!")
                #move_forward()
            #elif color == "white" and zone_navigation:
                #print("white! delivery mode!")
                #move_forward_small_zone()
            elif color == "white":
                #print("white!")
                if not return_loading_bay:
                    turn_right_white()
                else:
                    move_forward()
            elif color == "red":
                print("red!")
                if not return_loading_bay:
                    move_left_red()
                else:
                    turn_right()
            elif color == "blue":
                #print("blue!")
                if not return_loading_bay:
                    turn_right()
                else:
                    turn_left()
            elif color == "green" and not return_loading_bay and not zone_navigation:
                #print("green!")
                sleep_time = 0.6
                num = 1
                zone_navigation = True
            elif color == "green" and not return_loading_bay and zone_navigation:
                #print("green! delivery mode!")
                move_forward_small_zone()
            elif color == "green" and return_loading_bay:
                move_forward()
            elif color == "yellow" and return_loading_bay:
                print("yellow!")
                stop_system = True
                return_loading_bay = False
                turn_180()
                system_start()
            elif zone_navigation:
                move_forward_small_zone()
            else:
                move_forward_small()

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

## Drop-off Mechanism Code

#color detected by the color sensor 
delivery_color_index = -1
currentPosition = 2 #0 to 5 - starts at yellow 
rotationPerPositionConstant = -115
# position of cubes: 0 = red, 1 = orange, 2 = yellow, 3 = green, 4 = blue, 5 = pink

def read_input_drop_off(color):
    global delivery_color_index, block_pushed
    wait_ready_sensors()
    try:
        print("in read_input_drop_off")

        if color == "blue":
            print("blue!")
            delivery_color_index = 4
            if block_pushed[4] == False:
                block_pushed[4] = True
                moveConveyorBelt()
        if color == "green":
            print("green!")
            delivery_color_index = 3
            if block_pushed[3] == False:
                block_pushed[3] = True
                moveConveyorBelt()
        if color == "yellow":
            print("yellow!")
            delivery_color_index = 2
            if block_pushed[2] == False:
                block_pushed[2] = True
                moveConveyorBelt()
        if color == "red":
            print("red")
            delivery_color_index = 0
            if block_pushed[0] == False:
                block_pushed[0] = True
                moveConveyorBelt()
        if color == "orange":
            print("orange!")
            delivery_color_index = 1
            if block_pushed[1] == False:
                block_pushed[1] = True
                moveConveyorBelt()
        if color == "purple":
            print("purple!")
            delivery_color_index = 5
            if block_pushed[5] == False:
                block_pushed[5] = True
                moveConveyorBelt()
        else:
            move_forward_small()
        time.sleep(3)

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        CONVEYOR_BELT_MOTOR.set_position_relative(0)
        PUSH_MOTOR.set_position_relative(0)
        BP.reset_all()
        
#def set_detected_color_index(color):
    #global delivery_color_index
    #wait_ready_sensors()
    #try:
        #print("in read_input_drop_off")

        #if color == "blue":
            #print("blue!")
            #delivery_color_index = 4
        #if color == "green":
            #print("green!")
            #delivery_color_index = 3
        #if color == "yellow":
            #print("yellow!")
            #delivery_color_index = 2
        #if color == "red":
            #print("red")
            #delivery_color_index = 0
        #if color == "orange":
            #print("orange!")
            #delivery_color_index = 1
        #if color == "purple":
            #print("purple!")
            #delivery_color_index = 5
        #time.sleep(3)

    #except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        #CONVEYOR_BELT_MOTOR.set_position_relative(0)
        #PUSH_MOTOR.set_position_relative(0)
        #BP.reset_all()

def moveConveyorBelt():
    print("moveConveyorBelt entered")
    global delivery_color_index, currentPosition, rotationPerPositionConstant, rotations
    # move the conveyor belt so that the detected color is at the right position to push
    # this is where the logic for the conveyor belt will go

    # calculate the number of positions required to move 
    #numberOfPositions = currentPosition - detectedColor
    numberOfPositions = 2 - delivery_color_index
    # calculate the number of rotations required to move the conveyer belt
    rotations = numberOfPositions * rotationPerPositionConstant

    # Encoder keeps a record of degrees turned
    CONVEYOR_BELT_MOTOR.set_dps(70)
    CONVEYOR_BELT_MOTOR.set_position_relative(rotations)             # Rotate the desired amount of degrees
    
    time.sleep(5)
    pushCube() # push cube into delivery zone

def pushCube():
    global rotations
    # push cube into delivery zone
    # this is where the logic for the pusher will go
    print("push cube")
    # Encoder keeps a record of degrees turned
    PUSH_MOTOR.set_dps(90)
    PUSH_MOTOR.set_position_relative(-45) # Rotate negative rotation when pushing out cube 
    time.sleep(2)
    PUSH_MOTOR.set_dps(70)
    PUSH_MOTOR.set_position_relative(45) # Rotate back to original position
    time.sleep(2)
    
    CONVEYOR_BELT_MOTOR.set_dps(70)
    CONVEYOR_BELT_MOTOR.set_position_relative(-rotations)
    time.sleep(1)


if __name__ == "__main__":
    zone_navigation_thread = threading.Thread(target=zone_color_detection)
    zone_navigation_thread.start()
    motor_set_up()
    system_start()

