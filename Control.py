"""

"""
import pygame
import numpy as np
# import argparse
# import imutils
#import cv2

from curve import *
from Model import *

greenLower=(29, 86, 6)
greenUpper=(64, 255, 255)

class Controller(object):
	def __init__(self):
		self.modes=[None, 'Mouse drawing','Open CV drawing', "Mouse pulling"]
		#self.open_cv_control = Open_cv_control()
		self.running_points = []
		self.running = True
		self.curve = None
		self.last_space = False
		self.last_press = False
		self.last_g = False
		self.pull_point = None
		self.mode = None
		self.model = Model()


	def handle_events(self):
		# print self.mode
		# print self.running_points
		for event in pygame.event.get():	
			if event.type == pygame.QUIT:	# Handle window closing
				try: 
					self.open_cv_control.close_camera()
				except:
					print "OpenCV Not Loaded"
				self.running = False

		keys = pygame.key.get_pressed() # Returns a tuple of 1s and 0s corresponding to the the pressed keys

		if self.mode == None:
			if keys[pygame.K_SPACE] and not self.last_space: 
				self.mode = 'Open CV drawing'
				self.open_cv_control.running_points = []
				self.running_points = []
				self.curve = None

			if pygame.mouse.get_pressed()[0] and not self.last_press:

				if self.curve:

					mouse_pos = pygame.mouse.get_pos()

					hitbox_radius = 5

					for idx, pt in enumerate(self.curve.line.points):
						if abs(pt[0]-mouse_pos[0]) < hitbox_radius:
							self.pull_point = idx
							print "Pulling point is number:", idx
							self.mode = 'Mouse pulling'
				else:
					self.mode = 'Mouse drawing'
					self.running_points = []

		elif self.mode == 'Mouse drawing':

			self.draw_with_mouse()

			if pygame.mouse.get_pressed()[0] and not self.last_press: # Press Mouse1 to enter/leave Drawing mode
				self.mode = None
				if len(self.running_points)>15:
					self.curve = Curve(self.running_points[::len(self.running_points)/15])  #[::len(self.running_points)/15]
				else:
					print 'Not enough points registered'

		elif self.mode == 'Open CV drawing':
			try:
				self.open_cv_control.draw_with_open_cv()
			except:
				
				open_cv_control.close_camera()

			self.running_points = self.open_cv_control.running_points

			if keys[pygame.K_SPACE] and not self.last_space:
				self.mode = None
				if len(self.running_points)>15:
					self.curve = Curve(self.running_points[::len(self.running_points)/15])  #[::len(self.running_points)/15]
				else:
					print 'Not enough points registered'

		elif self.mode == "Mouse pulling":
			self.pull_with_mouse()

			if pygame.mouse.get_pressed()[0] and not self.last_press: # Press Mouse1 to enter/leave Drawing mode
				self.mode = None

		if pygame.mouse.get_pressed()[2]: # Mouse2 to clear
			self.mode = None
			self.running_points = []
			try:
				self.open_cv_control.running_points = []
			except:
				print "OpenCV Not Loaded"
			self.curve = None

		if keys[pygame.K_g] and not self.last_g:
			
			self.model.grid_update()

		self.last_space = keys[pygame.K_SPACE] # Keep track of the last Space 
		self.last_press = pygame.mouse.get_pressed()[0]
		self.last_g = keys[pygame.K_g]

	def draw_with_mouse(self):
		'''This method is currently called by view.draw_input()

		Allows the user to draw several lines/curves in discrete intervals with mouse. 
		Press leftbutton to start drawing, move around the mouse to draw (or hold down the lef button while drawing.
		Press leftbutton again to stop drawing. Press rightbutton to clear screen.

		running_points stores the points of the user's curve as nested lists. (if the user draws a single curve, it would be [[(x,y)...]]

		Next implementation would be to stop drawing when the leftbutton is released (MOUSEBUTTONUP doesn't work right now).'''

		mouse_pos = pygame.mouse.get_pos()
		# Add points based off of mouse position
		if not self.running_points:
			self.running_points.append(mouse_pos)

		if mouse_pos != self.running_points[-1] and self.running_points[-1][0] < mouse_pos[0]: # NOTE: This is where we check if the user goes backwards
			self.running_points.append(mouse_pos)


	def pull_with_mouse(self):
		# Get new mouse positions
		mouse_pos = pygame.mouse.get_pos()
		# Move point there
		# self.curve.line.move_point(self.pull_point, mouse_pos, kind='sigmoid')
		self.curve.move_point(self.pull_point, mouse_pos, line="line")

class Open_cv_control(object):
	def __init__(self):
		self.running_points = []
		self.camera = cv2.VideoCapture(0)
		print 'Initiated open CV'

	def draw_with_open_cv(self):
		# Grab the current frame (frame and masl are numpy.ndarray)
		(grabbed, frame) = self.camera.read()
		if grabbed:
			# Resize the frame, blur it, and convert it to the HSV color space
			frame = imutils.resize(frame, width=600)
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

			# Construct a mask for the color "green", then perform a series of dilations and erosions to remove any small
			# blobs left in the mask
			mask = cv2.inRange(hsv, greenLower, greenUpper)
			mask = cv2.erode(mask, None, iterations=2)
			mask = cv2.dilate(mask, None, iterations=2)

			# Flip the mask and frame horizontally
			hfmask = cv2.flip(mask,1)
			hfframe = cv2.flip(frame,1)

			# Find contours in the mask and initialize the current
			# (x, y) center of the ball
			cnts = cv2.findContours(hfmask.copy(), cv2.RETR_CCOMP,
				cv2.CHAIN_APPROX_SIMPLE)[-2]
			center = None
		# Only proceed if at least one contour was found
			if len(cnts) > 0:
				# Find the largest contour in the mask, then use
				# it to compute the minimum enclosing circle and
				# centroid
				c = max(cnts, key=cv2.contourArea)
				((x, y), radius) = cv2.minEnclosingCircle(c)

				# Only proceed if the radius meets a minimum size
				print radius
				if radius > 20:
					pts=(int(x),int(y))

					cv2.circle(hfframe, pts, int(radius),(0, 255, 255), 2)

					if not self.running_points:
						print 'appending points'
						self.running_points.append(pts)

					if pts != self.running_points[-1] and self.running_points[-1][0] < pts[0]: 	# Add point if it is different than the previous
						print 'appending points'
						self.running_points.append(pts)								# and if it doesn't curl back (last x < new x)
			
			for i in xrange(1, len(self.running_points)):
				# if either of the tracked points are None, ignore
				# them
				if self.running_points[i - 1] is None or self.running_points[i] is None:
					continue
				# otherwise, compute the thickness of the line and
				# draw the connecting lines
				thickness = 2
				cv2.line(hfframe, self.running_points[i - 1], self.running_points[i], (0, 0, 255), thickness)

			cv2.imshow("Mask", hfmask)
			cv2.imshow("Horizontal flip", hfframe)
			cv2.waitKey(1)
	def close_camera(self):
		self.camera.release()
		cv2.destroyAllWindows()


	
# '''This method is currently called by view.draw_input()

# 		Allows the user to draw several lines/curves in discrete intervals with mouse. 
# 		Press leftbutton to start drawing, move around the mouse to draw (or hold down the lef button while drawing.
# 		Press leftbutton again to stop drawing. Press rightbutton to clear screen.

# 		running_points stores the points of the user's curve as nested lists. (if the user draws a single curve, it would be [[(x,y)...]]

# 		Next implementation would be to stop drawing when the leftbutton is released (MOUSEBUTTONUP doesn't work right now).'''


# if __name__ == "main":
# 	for testing
# 	mouse=Mouse_control()
# 	counter=1
# 	while counter<1000:
# 		counter+=1
# 		mouse.handle_event()

