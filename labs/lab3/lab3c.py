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

isParked = False
speed = 0.0
angle = 0.0

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
    global isParked
    global speed
    global angle

    further_y_distance = 40

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    depth_image = (depth_image - 0.01) % 10000

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.
    cropped_camera_height = (rc.camera.get_height() // 2) * 1
    top_left_inclusive = (0, 0)
    bottom_right_exclusive = (cropped_camera_height, (rc.camera.get_width()))
    depth_image = rc_utils.crop(depth_image, top_left_inclusive, bottom_right_exclusive)
    depth_image = (depth_image - 0.01) % 10000

    # Retrieve the distance of the central pixel
    y, x = rc_utils.get_closest_pixel(depth_image)
    distance = depth_image[y, x]
    left_x = rc_utils.clamp(x - 40, 0, rc.camera.get_width() - 1)
    right_x = rc_utils.clamp(x + 40, 0, rc.camera.get_width() - 1)

    left_distance = depth_image[y, left_x]
    right_distance = depth_image[y, right_x]

    # Check if in distance to stop
    if distance < 19:
        angle *= -1
        speed = rc_utils.remap_range(distance, 0, 20, -1, 0)
        speed = np.clip(speed, -1, 1)
        isParked = False
        print("Backing up")

    # checks if the car is parked
    elif distance < 20:
        rc.drive.stop()
        speed = 0
        angle = 0
        isParked = True
        print("parked")

    else:
        if isParked == False:
            # Tries to set speed at the value corresponding to the contour center
            # If no contour center, then set speed to 0.2
            try:
                speed = rc_utils.remap_range(distance, 20, 500, 0, 1)
                speed = np.clip(speed, -1, 1)
            except:
                print("Speed Error: setting speed to 0.2")
                speed = 0.2

    # Use the left joystick to control the angle of the front wheels
    if isParked == False:
        angle = rc_utils.remap_range(x, 0, rc.camera.get_width(), -1, 1)
        multiplier = rc_utils.remap_range(distance, 20, 150, 3, 1)
        angle = rc_utils.clamp(angle * multiplier, -1, 1)
        print("multi:", multiplier, "angle:", angle)


    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    if rc.controller.is_down(rc.controller.Button.B):
        print("Center distance:", distance)

    # Display the current depth image
    rc.display.show_depth_image(depth_image, points=[(y, x), (y, right_x), (y, left_x)])


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
