"""

"""
import pygame
import numpy as np

try:
	import argparse
	import imutils
	import cv2
except:
	print "Open CV libraries not loaded."


from curve import *
from Model import *

#define HSV color range of a tennis ball: open cv has range: H: 0-180, S: 0 -255, V: 0-255
colors = {'bright_green':[(29, 84, 6),(64, 255, 255)],'bright_pink':[(145,84,120),(175,255,255)]}
color='bright_pink'

class Controller(object): 
	def __init__(self):
		self.modes=[None, 'Mouse drawing','Open CV drawing', "Mouse pulling", 'Open CV calibrating','Show tangent']

		try:
			self.open_cv_control = Open_cv_control()
		except:
			pass

		self.running_points = []
		self.running = True
		self.curve = None
		self.last_space = False
		self.last_press = False
		self.last_g = False
		self.last_l = False
		self.last_c = False
		self.pull_point = None
		self.mode = None
		self.model = Model()

		self.pull_mode = "Curve"
		self.image = None


	def handle_events(self):
		for event in pygame.event.get():	
			if event.type == pygame.QUIT:	# Handle window closing
				try: 
					self.open_cv_control.close_camera()
				except:
					print "OpenCV Not Loaded"
				self.running = False

		keys = pygame.key.get_pressed() # Returns a tuple of 1s and 0s corresponding to the the pressed keys
		
		hitbox_radius = 5 #for clicking on curves

		if self.mode == None:
			if keys[pygame.K_SPACE] and not self.last_space: 
				self.mode = 'Open CV drawing'
				self.open_cv_control.running_points = []
				self.running_points = []
				self.curve = None

			if keys[pygame.K_c] and not self.last_c:
				self.mode = 'Open CV calibrating'

			if pygame.mouse.get_pressed()[0] and not self.last_press:

				if self.curve:

					mouse_pos = pygame.mouse.get_pos()

					if self.pull_mode == "Handle":
						for idx, pt in enumerate(self.curve.line.pull_points):
							if abs(pt[0]-mouse_pos[0]) < hitbox_radius and abs(pt[1]-mouse_pos[1]) < hitbox_radius:
								self.pull_point = idx
								print "Pulling point is number:", idx
								self.mode = 'Mouse pulling'

					elif self.pull_mode == "Curve":
						for idx, pt in enumerate(self.curve.line.points):
							if abs(pt[0]-mouse_pos[0]) < hitbox_radius:
								self.pull_point = idx
								print "Pulling point is number:", idx
								self.mode = 'Mouse pulling'
				else:
					self.mode = 'Mouse drawing'
					self.running_points = []

			if keys[pygame.K_t] and not self.last_t:
				self.mode = 'Show tangent'

		elif self.mode == 'Mouse drawing':

			self.draw_with_mouse()

			if pygame.mouse.get_pressed()[0] and not self.last_press: # Press Mouse1 to enter/leave Drawing mode
				self.mode = None
				if len(self.running_points)>15:
					self.curve = Curve(self.running_points[::len(self.running_points)/7], self.pull_mode)  #[::len(self.running_points)/15]
				else:
					print 'Not enough points registered'

		elif self.mode == 'Open CV calibrating':
			self.open_cv_control.calibrate_color()
			if keys[pygame.K_c] and not self.last_c:
				self.mode = None

		elif self.mode == 'Open CV drawing':
			# try:
			self.open_cv_control.draw_with_open_cv()
			self.image = self.open_cv_control.image
			# except:	
			# 	self.open_cv_control.close_camera()

			self.running_points = self.open_cv_control.running_points

			if keys[pygame.K_SPACE] and not self.last_space:
				self.mode = None
				if len(self.running_points)>15:
					self.curve = Curve(self.running_points[::len(self.running_points)/15], self.pull_mode)  #[::len(self.running_points)/15]
					print self.running_points
				else:
					print 'Not enough points registered'

		elif self.mode == "Mouse pulling":
			self.pull_with_mouse()

			if pygame.mouse.get_pressed()[0] and not self.last_press: # Press Mouse1 to enter/leave Drawing mode
				self.mode = None
		
		elif self.mode == 'Show tangent':
			if pygame.mouse.get_pressed()[0]:
				mouse_pos = pygame.mouse.get_pos()

				for idx, pt in enumerate(self.curve.line.points):
					if abs(pt[0]-mouse_pos[0]) < hitbox_radius:
						self.tangent_point = idx
						self.curve.line.make_tangent(idx,100)

			if keys[pygame.K_t] and not self.last_t:
				self.mode = None

		elif self.mode == 'Show area':
			if pygame.mouse.get_pressed()[0]:
				mouse_pos = pygame.mouse.get_pos()

				for idx, pt in enumerate(self.curve.line.points):
					if abs(pt[0]-mouse_pos[0]) < hitbox_radius:
						self.curve.line.draw_area(idx) 


		'''Clearing the screen'''
		if pygame.mouse.get_pressed()[2]: # Mouse2 to clear
			self.mode = None
			self.running_points = []
			try:
				self.open_cv_control.running_points = []
			except:
				print "OpenCV Not Loaded"
			self.curve = None

		""" Stuff to change grid, legend etc."""
		if keys[pygame.K_g] and not self.last_g:
			self.model.grid_update()
		if keys[pygame.K_l] and not self.last_l:
			self.model.legend_update()


		self.last_space = keys[pygame.K_SPACE] # Keep track of the last Space 
		self.last_press = pygame.mouse.get_pressed()[0]
		self.last_g = keys[pygame.K_g]
		self.last_l = keys[pygame.K_l]
		self.last_c = keys[pygame.K_c]
		self.last_t = keys[pygame.K_t]

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
		self.camera.set(3,640) #setting camera size
		self.camera.set(4,480) #setting camera size
		self.prev_avg_col = (0,0,0)
		self.color = color
		self.draw_color_lower = colors[self.color][0]
		self.draw_color_upper = colors[self.color][1]
		self.image = None
		# self.display_window = True 
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
			mask = cv2.inRange(hsv, self.draw_color_lower, self.draw_color_upper)
			mask = cv2.erode(mask, None, iterations=2)
			mask = cv2.dilate(mask, None, iterations=2)

			# Flip the mask and frame horizontally so it's the direction of draw
			hfmask = cv2.flip(mask,1)
			hfframe = cv2.flip(frame,1) #flip if use open cv to display image

			# Find contours in the mask and initialize the current
			# (x, y) center of the balls
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
				# print radius
				if radius > 30:
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
				cv2.line(hfframe, self.running_points[i - 1], self.running_points[i], (255, 0, 0), thickness)
			
			self.image = cv2.cvtColor(hfframe,cv2.COLOR_BGR2RGB)
			self.image = cv2.flip(self.image,1) #flip the image back for pygame display and rotate the image 
			self.image = np.rot90(self.image) 

			# if self.display_window:
			cv2.imshow("Mask", hfmask)
			cv2.imshow("Horizontal flip", hfframe)
			cv2.waitKey(1)  #waitKey displays each image for 1 ms. and allow the loop to run. if itt's 0 the image will be displayed infinitely and no input will be accepted
			# key = cv2.waitKey(1)
			# if key == ord("q"):
			# 	self.display_window = False

	def calibrate_color(self):
		(grabbed, frame) = self.camera.read()
		if grabbed:
			frame_size = frame.shape
			frame_ct = (frame_size[1]/2,frame_size[0]/2)
			# print frame_ct
			# pixels = [frame[i,j] for i in range(frame_ct[0]-10,frame_ct[0]+10) for j in range(frame_ct[1]-10,frame_ct[1]+10)]
			# self.avg_col= (int(np.mean([px[0] for px in pixels])),int(np.mean([px[1] for px in pixels])),int(np.mean([px[2] for px in pixels])))
			# if self.avg_col != self.prev_avg_col:
			# 	print self.avg_col
			# self.prev_avg_col = self.avg_col
			print frame[frame_ct[0],frame_ct[1]]
			cv2.circle(frame, frame_ct, 20,(142, 37, 149), -1) #bright pink color

			cv2.rectangle(frame, (frame_ct[0]-50,frame_ct[1]-50),(frame_ct[0]+50,frame_ct[1]+50), (0,255,255),2)
			cv2.imshow('Frame',frame)
			cv2.waitKey(1)


	def close_camera(self):
		self.camera.release()
		cv2.destroyAllWindows()


	

# if __name__ == "main":
# 	for testing
# 	c = Open_cv_control()
# 	Open_cv_control.calibrate_color()
# 	if 

