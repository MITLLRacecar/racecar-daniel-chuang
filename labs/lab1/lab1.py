"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 1 - Driving in Shapes
"""

########################################################################################
# Imports
########################################################################################

import sys

sys.path.insert(1, "../../library")
import racecar_core
# import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Put any global variables here

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    rc.drive.stop()

    # Print start message
    # TODO (main challenge): add a line explaining what the Y button does
    print(
        ">> Lab 1 - Driving in Shapes\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = drive in a circle\n"
        "    B button = drive in a square\n"
        "    X button = drive in a figure eight\n"
        "    Y button = drive in a wave\n"
    )
    

# Setting up constants
counter = 0
driveA = False
driveB = False
driveX = False
driveY = False
turnTimeIncrement = 6.3
forwardsTimeIncrement = 5
limits = [0]


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # Use global constants
    global counter
    global driveA
    global driveB
    global driveX
    global driveY
    
    # for square challenge
    global turnTimeIncrement
    global forwardsTimeIncrement
    global limits
    
    # TODO (warmup): Implement manual acceleration and steering
    manual_speed = 0
    manual_angle = 0

    manual_speed -= rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    manual_speed += rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    manual_angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    
    # print(manual_speed, manual_angle)
    rc.drive.set_speed_angle(manual_speed, manual_angle)
    
    
    # TODO (main challenge): Drive in a circle
    if rc.controller.was_pressed(rc.controller.Button.A):
        print("Driving in a circle...")
        driveA = True
        counter = 0

    if driveA == True:
        rc.drive.set_speed_angle(0.5, -1)
        counter += rc.get_delta_time()
        
        if counter > 11.7:
            rc.drive.stop()
            driveA = False
            print("STOPPED CIRCLE")
    
    
    # TODO (main challenge): Drive in a square when the B button is pressed
    if rc.controller.was_pressed(rc.controller.Button.B):
        print("Driving in a square...")
        counter = 0
        driveB = True
        limits = [0]
        for i in range(8):
            if i % 2 == 0:
                limits.append(limits[-1] + forwardsTimeIncrement)
            else:
                limits.append(limits[-1] + turnTimeIncrement)
        print(limits)
        limits[1] += 1
    
    if driveB == True:
        forward_speed = 0.5
        turn_speed = 0.15
        
        counter += rc.get_delta_time()

        if counter < limits[1]:
            rc.drive.set_speed_angle(forward_speed, 0)

        elif counter < limits[2]:
            rc.drive.set_speed_angle(turn_speed, -1)

        elif counter < limits[3]:
            rc.drive.set_speed_angle(forward_speed, 0)

        elif counter < limits[4]:
            rc.drive.set_speed_angle(turn_speed, -1)

        elif counter < limits[5]:
            rc.drive.set_speed_angle(forward_speed, 0)

        elif counter < limits[6]:
            rc.drive.set_speed_angle(turn_speed, -1)

        elif counter < limits[7]:
            rc.drive.set_speed_angle(forward_speed, 0)

        elif counter < limits[8]:
            rc.drive.set_speed_angle(turn_speed, -1)

        else:
            driveB = False
            rc.drive.stop()
            print("STOPPED SQUARE")


    # TODO (main challenge): Drive in a figure eight when the X button is pressed
    if rc.controller.was_pressed(rc.controller.Button.X):
        print("Driving in a figure eight...")
        driveX = True
        counter = 0

    if driveX == True:
        rc.drive.set_speed_angle(0.5, -1)
        counter += rc.get_delta_time()
        
        if counter < 11.7:
            rc.drive.set_speed_angle(0.5, 1)

        elif counter > 23.4:
            rc.drive.stop()
            driveX = False
            print("STOPPED FIGURE EIGHT")

    # TODO (main challenge): Drive in a shape of your choice when the Y button
    # is pressed
    if rc.controller.was_pressed(rc.controller.Button.Y):
        print("Driving in a wave...")
        driveY = True
        counter = 0
        
    if driveY == True:
        print(counter)
        counter += rc.get_delta_time()
        
        if counter < 3:
            rc.drive.set_speed_angle(1, -1)
        
        elif counter < 6:
            rc.drive.set_speed_angle(1, 1)

        elif counter < 9:
            rc.drive.set_speed_angle(1, -1)

        elif counter < 12:
            rc.drive.set_speed_angle(1, 1)

        elif counter < 15:
            rc.drive.set_speed_angle(1, -1)
        
        else:
            driveY = False
            rc.drive.stop()
            print("STOPPED WAVE")


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
