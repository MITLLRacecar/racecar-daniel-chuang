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

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

########################################################################################
# Global variables
########################################################################################

RED = ((160, 0, 0), (179, 255, 255)) # NOTE: THIS IS ON THE OTHER SIDE OF THE HUE WHEEL!
BLUE = ((90, 120, 120), (120, 255, 255))

########################################################################################
# Utility Functions
########################################################################################

def update_contours(color_image, colors: list):
	"""
	Takes a color_image.

	Returns a list of contours on that color_image for each color specified.
	"""
	contours = []
	for color in colors:
		contours += rc_utils.find_contours(color_image, color[0], color[1])

	return contours

def closest_contour_center(depth_image, contours):
	"""
	Takes a depth_image and list of contours.

	Finds the center of each contour, then finds which center is closest.

	Returns the coordinates for that center in y, x format.
	"""
	contour_centers = []
	for contour in contours:
		contour_centers.append(rc_utils.get_contour_center(contour))

	if len(contour_centers) == 0:
		return None

	# Set the closest so far to be very high
	closest_distance = 10000
	index = 0
	for i in range(len(contour_centers)):
		if contour_centers[i] == None:
			continue
		distance = rc_utils.get_pixel_average_distance(depth_image, contour_centers[i], 3)
		if distance < closest_distance and distance > 1:
			closest_distance = distance
			index = i

	return contour_centers[index]

def get_coordinate_color(color_image, coordinate, colors: list):
	"""
	Takes a color_image, coordinate (tuple), and list of color thresholds in HSV.

	If the pixel is within a color threshold, return the index of the color in the list.

	Coordinate should be in y, x format.
	"""
	try:
		if coordinate == None:
			return None
	except:
		pass

	color_image = cv.cvtColor(color_image, cv.COLOR_BGR2HSV)
	coordinate_color = color_image[coordinate[0], coordinate[1]]

	for i in range(len(colors)):
		color = np.array(colors[i])
		truth_array = np.logical_and(coordinate_color >= color[0], coordinate_color <= color[1])
		if np.all(truth_array):
			return i
	
	return None # return none if not in any colors

########################################################################################
# Environment Interaction Functions
########################################################################################

def start():
	"""
	Runs upon starting the script in the environment.
	"""
    # Have the car begin at a stop
	rc.drive.stop()

    # Print start message
	print(">> Phase 1 Challenge: Cone Slaloming")

def update():
	"""
	Runs constantly while script is running in the environment.
	"""
	# Get color and depth images
	depth_image = rc.camera.get_depth_image()
	color_image = rc.camera.get_color_image()
    
	# Set variables equal to the width and height for further calculations
	camera_height = (rc.camera.get_height() // 10) * 10 # Can crop with these numbers
	camera_width = (rc.camera.get_width() // 10) * 10

	# Retrieve the contours
	colors = [RED, BLUE]
	contours = update_contours(color_image, colors)

	# Retrieve the closest contour center
	contour_center = closest_contour_center(depth_image, contours)

	# Get the color value of the closest contour center
	contour_center_color = get_coordinate_color(color_image, contour_center, colors)
	
	if contour_center_color == None:
		contour_center_color = "NONE"
	else:
		contour_center_color = colors[contour_center_color]
		if contour_center_color == RED:
			contour_center_color = "RED"
		else:
			contour_center_color = "BLUE"

	# Display Camera
	if contour_center is not None:
		rc_utils.draw_circle(color_image, contour_center)
	rc.display.show_color_image(color_image)

	# MANUAL CONTROLS
	# '''
	manual_speed = 0
	manual_angle = 0

	manual_speed -= rc.controller.get_trigger(rc.controller.Trigger.LEFT)
	manual_speed += rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
	manual_angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    
	rc.drive.set_speed_angle(manual_speed, manual_angle)
	# '''

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()