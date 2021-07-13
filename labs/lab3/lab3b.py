"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3B - Depth Camera Cone Parking
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
# Sets up the racecar object
rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# The HSV range for the color orange, stored as (hsv_min, hsv_max)
ORANGE = ((10, 100, 100), (20, 255, 255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

# Add any global variables here
isParked = False # Set to true once the car has stopped around 30cm in front of the cone

########################################################################################
# Functions
########################################################################################
def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Find all of the orange contours
        contours = rc_utils.find_contours(image, ORANGE[0], ORANGE[1])

        # Select the largest contour
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            # Calculate contour information
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)

        else:
            contour_center = None
            contour_area = 0

def get_mask(
    image: NDArray[(Any, Any, 3), np.uint8],
    hsv_lower: Tuple[int, int, int],
    hsv_upper: Tuple[int, int, int]
) -> NDArray[Any, Any]:
    """
    Returns a mask containing all of the areas of image which were between hsv_lower and hsv_upper.

    Args:
        image: The image (stored in BGR) from which to create a mask.
        hsv_lower: The lower bound of HSV values to include in the mask.
        hsv_upper: The upper bound of HSV values to include in the mask.
    """
    # Convert hsv_lower and hsv_upper to numpy arrays so they can be used by OpenCV
    hsv_lower = np.array(hsv_lower)
    hsv_upper = np.array(hsv_upper)

    # TODO: Use the cv.cvtColor function to switch our BGR colors to HSV colors
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # TODO: Use the cv.inRange function to highlight areas in the correct range
    mask = cv.inRange(image, hsv_lower, hsv_upper)

    return mask

def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(">> Lab 3B - Depth Camera Cone Parking")

def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 30 cm away from the closest orange cone.
    global speed
    global angle
    global isParked

    # Search for contours in the current color image
    update_contour()

    # TODO: Park the car 30 cm away from the closest orange cone
    # Tries to turn at the angle corresponding to the contour center
    # If no contour center, then turn at an angle of 0.3
    try:
        angle = rc_utils.remap_range(contour_center[1], 0, rc.camera.get_width(), -1, 1)
    except:
        print("Angle Error: setting angle to 0.3")
        angle = 0.3

    # Gets a depth image, and filters for noise and null values
    depth_image = rc.camera.get_depth_image()

    # Crops the depth image
    top_left_inclusive = (0, 0)
    bottom_right_exclusive = ((rc.camera.get_height() // 10) * 9, rc.camera.get_width())


	# Using the color camera to mask the depth camera
    image = rc.camera.get_color_image()
    mask = get_mask(image, ORANGE[0], ORANGE[1])
    masked_depth_image = cv.bitwise_and(depth_image, depth_image, mask=mask)
    masked_depth_image = (masked_depth_image - 0.01) % 10000

    # Gets the distance to the closest value in the new masked depth image
    cropped_image = rc_utils.crop(masked_depth_image, top_left_inclusive, bottom_right_exclusive)
    rc.display.show_depth_image(cropped_image)
    y, x = rc_utils.get_closest_pixel(cropped_image)
    distance = cropped_image[y, x]
    print(distance)

    # Checks if car overshot parking and backs up
    if distance < 29:
        angle *= -1
        speed = rc_utils.remap_range(distance, 0, 30, -1, 0)
        speed = np.clip(speed, -1, 1)
        isParked = False
        print("Backing up")

    # checks if the car is parked
    elif distance < 30:
        rc.drive.stop()
        speed = 0
        angle = 0
        isParked = True
        print("parked")

    else:
        if not isParked:
            # Tries to set speed at the value corresponding to the contour center
            # If no contour center, then set speed to 0.2
            try:
                speed = rc_utils.remap_range(distance, 30, 500, 0, 1)
                speed = np.clip(speed, -1, 1)
            except:
                print("Speed Error: setting speed to 0.2")
                speed = 0.2

    # Set the speed and angle of the car according to all our calculatings!
    print(speed)
    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.Y):
        isParked = False
        print("not parke")
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)
    pass


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
