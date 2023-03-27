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
    
def move_forward_small():
    print("straight!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(15)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(15)
    time.sleep(1)
    
def move_forward_small_zone():
    print("straight!")
    LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(150)
    LEFT_MOTOR.set_position_relative(45)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(45)
    time.sleep(1)

def stop_moving():
    print("stop!")
    global delivery_count
#     LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
#     RIGHT_MOTOR.set_dps(150)
#     LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
#     RIGHT_MOTOR.set_position_relative(180)
    # get delivery zone color
    time.sleep(1)
#     move_forward()
#     print("first move forward")
    drop_off_zone_navigation()
    red, green, blue, trp = COLOR_SENSOR_2.get_value() # getting each R,G,B color
    color = cddz.get_delivery_zone_color(red, green, blue) # getting the color from color detection delivery zone
    # call the delivery drop-off mechanism
    read_input_drop_off(color)
    # move straight forward from green line
#     LEFT_MOTOR.set_dps(150)                              # Set the speed for the motor
#     RIGHT_MOTOR.set_dps(150)
#     LEFT_MOTOR.set_position_relative(180)             # Rotate the desired amount of degrees
#     RIGHT_MOTOR.set_position_relative(180)
    time.sleep(1)
    
    delivery_count += 1
    
def drop_off_zone_navigation():
    global return_loading_bay, stop_system, delivery_count, detectedColor
    wait_ready_sensors()
    try:
        while True:
            print("navigation while True drop off")
            
            red2, green2, blue2, trp2 = COLOR_SENSOR_2.get_value()
            color2 = cddz.get_delivery_zone_color(red2, green2, blue2)
            set_detected_color_index(color2)
            print(color2 + ": drop off zone color")
            if color2 != "white":
                print("potential drop off zone detected")
                if block_pushed[detectedColor] == True:
                    print("already pushed")
                else:
                    print("new color zone detected")
                    break
            
            time.sleep(1)
            red, green, blue, trp = COLOR_SENSOR_1.get_value() # getting each R,G,B color
            color = cdn.get_navigation_color(red, green, blue) # getting the color from color detection navigation

            if color == "white":
                print("move forward white!")
                move_forward_small_zone()
            if color == "blue":
                print("turn right blue!")
                if not return_loading_bay:
                    turn_right()
                else:
                    turn_left()
            if color == "red":
                print("turn left red!")
                if not return_loading_bay:
                    turn_left()
                else:
                    turn_right()
            if color == "green" and not return_loading_bay:
                print("move forward green!")
                move_forward_small_zone()
            if color == "yellow" and return_loading_bay:
                print("turn yellow!")
                stop_system = True
                turn_180()
                system_start()
            else:
               move_forward_small_zone() 
                
#             else:
#                 print("move forward white!")
#                 move_forward()


    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

def turn_180():
    print("Turning 180 degrees!")
    LEFT_MOTOR.set_dps(90)                              # Set the speed for the motor
    RIGHT_MOTOR.set_dps(90)
    LEFT_MOTOR.set_position_relative(0)             # Rotate the desired amount of degrees
    RIGHT_MOTOR.set_position_relative(1440)
    time.sleep(15)

def navigation():
    global return_loading_bay, stop_system, delivery_count
    wait_ready_sensors()
    try:
        while True:
            print("navigation while True")
            # check if all deliveries have been made
            if delivery_count == 6:
                return_loading_bay = True
                turn_180()
                delivery_count = 0

            time.sleep(1)
            red, green, blue, trp = COLOR_SENSOR_1.get_value() # getting each R,G,B color
            color = cdn.get_navigation_color(red, green, blue) # getting the color from color detection navigation

            if color == "white":
                print("white!")
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
            if color == "green" and return_loading_bay:
                move_forward()
            if color == "yellow" and return_loading_bay:
                #print("yellow!")
                stop_system = True
                turn_180()
                system_start()
            else:
                move_forward_small()
                
#             else: #white
#                 print("white!")
#                 move_forward()
                


    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        BP.reset_all()

## Drop-off Mechanism Code

#color detected by the color sensor 
detectedColor = -1
currentPosition = 2 #0 to 5 - starts at yellow 
rotationPerPositionConstant = -115
# position of cubes: 0 = red, 1 = orange, 2 = yellow, 3 = green, 4 = blue, 5 = pink

def read_input_drop_off(color):
    global detectedColor, block_pushed
    wait_ready_sensors()
    try:
        print("in read_input_drop_off")

        if color == "blue":
            print("blue!")
            detectedColor = 4
            if block_pushed[4] == False:
                block_pushed[4] = True
                moveConveyorBelt()
        if color == "green":
            print("green!")
            detectedColor = 3
            if block_pushed[3] == False:
                block_pushed[3] = True
                moveConveyorBelt()
        if color == "yellow":
            print("yellow!")
            detectedColor = 2
            if block_pushed[2] == False:
                block_pushed[2] = True
                moveConveyorBelt()
        if color == "red":
            print("red")
            detectedColor = 0
            if block_pushed[0] == False:
                block_pushed[0] = True
                moveConveyorBelt()
        if color == "orange":
            print("orange!")
            detectedColor = 1
            if block_pushed[1] == False:
                block_pushed[1] = True
                moveConveyorBelt()
        if color == "purple":
            print("purple!")
            detectedColor = 5
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
        
def set_detected_color_index(color):
    global detectedColor
    wait_ready_sensors()
    try:
        print("in read_input_drop_off")

        if color == "blue":
            print("blue!")
            detectedColor = 4
        if color == "green":
            print("green!")
            detectedColor = 3
        if color == "yellow":
            print("yellow!")
            detectedColor = 2
        if color == "red":
            print("red")
            detectedColor = 0
        if color == "orange":
            print("orange!")
            detectedColor = 1
        if color == "purple":
            print("purple!")
            detectedColor = 5
        time.sleep(3)

    except KeyboardInterrupt: # Program exit on ^C (Ctrl + C)
        CONVEYOR_BELT_MOTOR.set_position_relative(0)
        PUSH_MOTOR.set_position_relative(0)
        BP.reset_all()

def moveConveyorBelt():
    print("moveConveyorBelt entered")
    global detectedColor, currentPosition, rotationPerPositionConstant, rotations
    # move the conveyor belt so that the detected color is at the right position to push
    # this is where the logic for the conveyor belt will go

    # TODO - find rotation required to move conveyer belt 1 position 
    # calculate the number of positions required to move 
    #numberOfPositions = currentPosition - detectedColor
    numberOfPositions = 2 - detectedColor
    # calculate the number of rotations required to move the conveyer belt
    rotations = numberOfPositions * rotationPerPositionConstant

    # Encoder keeps a record of degrees turned
    #CONVEYOR_BELT_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    #CONVEYOR_BELT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits                             # Set the speed for the motor
    #CONVEYOR_BELT_MOTOR.set_dps(SPEED)
    #CONVEYOR_BELT_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT)
    CONVEYOR_BELT_MOTOR.set_dps(70)
    CONVEYOR_BELT_MOTOR.set_position_relative(rotations)             # Rotate the desired amount of degrees
    
    time.sleep(5)
    #CONVEYOR_BELT_MOTOR.set_power(0)
    pushCube() # push cube into delivery zone

    # update currentPosition 
    #currentPosition = detectedColor

def pushCube():
    global rotations
    # push cube into delivery zone
    # this is where the logic for the pusher will go
    print("push cube")
    # Encoder keeps a record of degrees turned
    #PUSH_MOTOR.reset_encoder()                      # Reset encoder to 0 value
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED_LIMIT) # Set the power and speed limits
    #PUSH_MOTOR.set_dps(SPEED)                              # Set the speed for the motor
    #PUSH_MOTOR.set_limits(POWER_LIMIT, SPEED)
    PUSH_MOTOR.set_position_relative(-50) # Rotate negative rotation when pushing out cube 
    time.sleep(2)
    PUSH_MOTOR.set_position_relative(50) # Rotate back to original position
    time.sleep(2)
    
    CONVEYOR_BELT_MOTOR.set_dps(70)
    CONVEYOR_BELT_MOTOR.set_position_relative(-rotations)
    time.sleep(1)


if __name__ == "__main__":
    motor_set_up()
    system_start()

