"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Phase 1 Challenge - Cone Slaloming
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import Enum

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################
class Mode(Enum):
    searching = 0
    red = 1
    blue = 2
    linear = 3

class Color(Enum):
    RED = 0
    BLUE = 1
    BOTH = 2

curr_mode = Mode.searching
color_priority = Color.RED

speed = 0.0
angle = 0.0
last_distance = 0

counter = 0

rc = racecar_core.create_racecar()

RED = ((160, 0, 0), (179, 255, 255)) # NOTE: THIS IS ON THE OTHER SIDE OF THE HUE WHEEL!
BLUE = ((90, 120, 120), (120, 255, 255))

########################################################################################
# Utility Functions
########################################################################################

def update_contours(color_image):
    """
    Finds contoours for the blue and red cone using color image
    """

    MIN_CONTOUR_AREA = 800

    # If no image is fetched
    if color_image is None:
        contour_center = None
        contour_area = 0

    # If an image is fetched successfully
    else:
        # Find all of the red contours
        contours_R = rc_utils.find_contours(color_image, RED[0], RED[1])

        # Find all of the blue contours
        contours_B = rc_utils.find_contours(color_image, BLUE[0], BLUE[1])

        # Select the largest contour from red and blue contours
        contour_R = rc_utils.get_largest_contour(contours_R, MIN_CONTOUR_AREA)
        contour_B = rc_utils.get_largest_contour(contours_B, MIN_CONTOUR_AREA)
        #print(rc_utils.get_contour_area(contour_B))

        # Draw a dot at the center of this contour in red
        if contour_R is not None and contour_B is not None: # checks if both are valid

            contour_area_R = rc_utils.get_contour_area(contour_R)
            contour_area_B = rc_utils.get_contour_area(contour_B)
            # if the contour areas are similar enough, indicate that it is a checkpoint
            if abs(contour_area_R - contour_area_B) < 700:
                print(abs(contour_area_R - contour_area_B))
                return None, Color.BOTH

            # If red contour is bigger than the blue one
            elif contour_area_R > contour_area_B:
                return contour_R, Color.RED

            # If blue contour is equal to or bigger than the red one
            else:
                return contour_B, Color.BLUE

        elif contour_R is None and contour_B is not None:
            return contour_B, Color.BLUE

        elif contour_B is None and contour_R is not None: 
            return contour_R, Color.RED

        else:
            # No contours found
            return None, None

########################################################################################
# Environment Interaction Functions
########################################################################################

def start():
    """
    This function is run once every time the start button is pressed
    """

    # Globals
    global curr_mode

    # Have the car begin at a stop
    rc.drive.stop()
    curr_mode = Mode.searching
    rc.drive.set_max_speed(0.75)

    # Print start message
    print(">> Phase 1 Challenge: Cone Slaloming")

def update_slow():
	pass

def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed

    Working with depth camera, fetching contour stuff from update_contours
    """

    # Globals
    global curr_mode
    global speed
    global angle
    global color_priority
    global last_distance
    global counter

    # Reset speed and angle variables
    speed = 0.0
    angle = 0.0
    distance = 5000
    speed_multiplier = 1
    distance_param = 200

    # TODO: Slalom between red and blue cones.  The car should pass to the right of
    # each red cone and the left of each blue cone.

    # Fetching images
    depth_image = rc.camera.get_depth_image()
    color_image = rc.camera.get_color_image()

    # Get camera sizes
    camera_height = (rc.camera.get_height() // 10) * 10
    camera_width = (rc.camera.get_width() // 10) * 10

    top_left_inclusive = (0, rc.camera.get_width() - camera_width)
    bottom_right_exclusive = ((camera_height, camera_width))

    # Cropping both images
    rc_utils.crop(color_image, top_left_inclusive, bottom_right_exclusive)
    rc_utils.crop(depth_image, top_left_inclusive, bottom_right_exclusive)

    # Getting contours from update_contours()
    contour, color = update_contours(color_image)

    # Copy the image
    color_image_display = np.copy(color_image)
    if contour is not None:
        # Getting contour center
        contour_center = rc_utils.get_contour_center(contour)

        # Drawing a color image with the contour
        rc_utils.draw_contour(color_image_display, contour)
        rc_utils.draw_circle(color_image_display, contour_center)

        # Calculate distance
        distance = rc_utils.get_pixel_average_distance(depth_image, contour_center)
        last_distance = distance
        print(f"Distance: {distance}")

    else:
        curr_mode = Mode.searching

    # Setting the current state
    if color == Color.RED:
        curr_mode = Mode.red
        color_priority = Color.RED
    elif color == Color.BLUE:
        curr_mode = Mode.blue
        color_priority = Color.BLUE
    elif color == Color.BOTH:
        curr_mode = Mode.linear
    else:
        curr_mode = Mode.searching


    # Check current mode and implement the respective actions
    if curr_mode == Mode.red and (distance < distance_param):
        # TODO: Red Cone Logic -> drive right to avoid
        angle = rc_utils.remap_range(contour_center[1], 0, camera_width, 0.3, 1)
        angle *= rc_utils.remap_range(last_distance, 200, 50, 0, 2)
        print("RED, ANGLE:", angle)
        counter = 0
    elif curr_mode == Mode.blue and (distance < distance_param):
        # TODO: Blue Cone Logic -> drive left to avoid
        angle = rc_utils.remap_range(contour_center[1], 0, camera_width, -1, -0.3)
        angle *= rc_utils.remap_range(last_distance, 50, 200, 2, 0)
        print("BLUE, ANGLE:", angle)
        counter = 0
    elif (curr_mode == Mode.blue or curr_mode == Mode.red) and distance >= distance_param:
        if curr_mode == Mode.blue:
            angle = rc_utils.remap_range(contour_center[1], 0, camera_width, -1, 1)
        elif curr_mode == Mode.red:
            angle = rc_utils.remap_range(contour_center[1], 0, camera_width, -1, 1)
        print("waiting")
        counter = 0
    elif curr_mode == Mode.linear:
        print("got here")
        angle = 0
        counter = 0
    else:
        if color_priority == Color.RED:
            angle = rc_utils.remap_range(last_distance, 0, 100, -0.3, -0.65) # drive left to return
        else:
            angle = rc_utils.remap_range(last_distance, 0, 100, 0.3, 0.65) # drive right to return


    ###########
    # TEMP MANUAL CONTROLS
    ###########
    #speed -= rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    #speed += rc.controller.get_trigger(rc.controller.Trigger.RIGHT)


    # Clamping functions
    angle = rc_utils.clamp(angle, -1, 1)
    speed = rc_utils.remap_range(abs(angle), 0, 1, 1, 0.05)
    speed = rc_utils.remap_range(last_distance, 60, 150, 0.1, 0.98)
    speed *= speed_multiplier
    speed = rc_utils.clamp(speed, -1, 1)


    # Displaying the color camera that was drawn on
    rc.display.show_color_image(color_image_display)

    # Setting the speed and angle of the car
    rc.drive.set_speed_angle(speed, angle)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()