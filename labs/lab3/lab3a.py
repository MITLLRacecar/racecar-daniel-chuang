"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3A - Depth Camera Safety Stop
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from typing import Any, Tuple, List, Optional
from nptyping import NDArray
sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here

isBackingUp = False

########################################################################################
# Functions
########################################################################################
def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(
        ">> Lab 3A - Depth Camera Safety Stop\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Right bumper = override safety stop\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = print current speed and angle\n"
        "    B button = print the distance at the center of the depth image"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global isBackingUp

    further_y_distance = 40

    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    depth_image = (depth_image - 0.01) % 10000

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.
    cropped_camera_height = (rc.camera.get_height() // 3) * 2
    top_left_inclusive = (0, rc.camera.get_width() // 4)
    bottom_right_exclusive = (cropped_camera_height, (rc.camera.get_width() // 4) * 3)
    depth_image = rc_utils.crop(depth_image, top_left_inclusive, bottom_right_exclusive)
    depth_image = (depth_image - 0.01) % 10000

    # Retrieve the distance of the central pixel
    y, x = rc_utils.get_closest_pixel(depth_image)
    distance = depth_image[y, x]
    further_y = rc_utils.clamp(y - 40, 0, cropped_camera_height)

    further_distance = depth_image[further_y, x]

    # Check if in distance to stop
    ang_vel = rc.physics.get_linear_acceleration()
    print(ang_vel)

    if distance < 60 and not rc.controller.is_down(rc.controller.Button.RB):
        if not further_distance > distance + 5:
            print("STOP INITIALIZED at", further_distance - distance)
            isBackingUp = True
            speed = - 1


    # Use the left joystick to control the angle of the front wheels
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    if rc.controller.is_down(rc.controller.Button.B):
        print("Center distance:", distance)

    # Display the current depth image
    rc.display.show_depth_image(depth_image, points=[(y, x), (further_y, x)])

    # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
    # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
