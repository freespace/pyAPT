# -*- coding: utf-8 -*-
'''
@brief Class that represents a Thorlabs 3D linear stage.
       It allows the user to perform different types of scans throught
		 the workspace.
@author Luis Carlos Garcia-Peraza Herrera <luis.herrera.14@ucl.ac.uk>
@author Efthymios Maneas <efthymios.maneas.14@ucl.ac.uk>

The coordinate system of the 3D linear stage is as follows:

	Top view:			Right view:							Front view:
	---------			-----------							-----------
											
	Motor controllers
	 __  __  __
	|__||__||__|		

	Y						Z										Z
	^						^										^ 
	|						|        						 	|  __  __  __
	|						|           __						| |  ||  ||  |
	o-----> X			o-----> Y  |__|					o-----> X 

Pre-requisites:
	
	1) pip install --upgrade matplotlib
	2) pip install --upgrade mpl_toolkits
	3) Run this command before executing this script:
			export PYTHONPATH=/Library/Python/2.7/site-packages

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import pyAPT
import threading
import time
import yaml
import sys
from math import *
from runner import runner_serial
from matplotlib import pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

class LinearStage(object):

	'''
	@brief Loading configuration from config file. 
	'''
	def __init__(self):
		config = yaml.load(open("configfile.yml")) # $ pip install pyyaml
		
		# Reading linear stage serial number from config file
		self.X_AXIS_SN = config["X_AXIS_SN"]
		self.Y_AXIS_SN = config["Y_AXIS_SN"]
		self.Z_AXIS_SN = config["Z_AXIS_SN"]
		
		# Reading distance range and scaling from config file
		self.MAX_DIST = config["MAX_DIST"]
		self.ENCODER_SCALE = config["ENCODER_SCALE"]
		self.MAX_DIST_ENCODER = self.MAX_DIST * self.ENCODER_SCALE

		# Moving 3D Stage Flags
		self.RIGHT = 0
		self.LEFT = 1
		self.DOWN = 0
		self.UP = 1

		# Plotting stuff
		self.fig = plt.figure()
		plt.ion()
		self.ax = self.fig.gca(projection = '3d')
		self.ax.set_xlim3d(0, self.MAX_DIST)
		self.ax.set_ylim3d(0, self.MAX_DIST)
		self.ax.set_zlim3d(0, self.MAX_DIST)
		# self.ax.view_init(elev = 45, azim = 90)

	def getInfoAxis(self, axis):
		con = pyAPT.MTS50(serial_number = axis)
		ret = con.info()
		con.close()
		return ret

	'''
	@brief Prints the serial number, model, type, firmware version and servo of all the connected stages.
	'''
	def getInfo(self):
		labels = ['S/N','Model','Type','Firmware Ver', 'Notes', 'H/W Ver', 'Mod State', 'Channels']
		xInfo = self.getInfoAxis(self.X_AXIS_SN)
		yInfo = self.getInfoAxis(self.Y_AXIS_SN)
		zInfo = self.getInfoAxis(self.Z_AXIS_SN)
		print("\nInformation of the X axis:")
		print('--------------------------')
		for idx, ainfo in enumerate(xInfo):
			print(("\t%12s: %s" % (labels[idx], bytes(ainfo))))
		print("\nInformation of the Y axis:")
		print('--------------------------')
		for idx, ainfo in enumerate(yInfo):
			print(("\t%12s: %s" % (labels[idx], bytes(ainfo))))
		print("\nInformation of the Z axis:")
		print('--------------------------')
		for idx, ainfo in enumerate(zInfo):
			print(("\t%12s: %s" % (labels[idx], bytes(ainfo))))
		print("\n")

	'''
	@brief Obtains the current position, velocity and status of a linear stage connected through USB.
	@param[in] axis Serial number of the target linear stage.
	@returns Status for the stage with the serial number provided.
	'''
	def getStatusAxis(self, axis):
		con = pyAPT.MTS50(serial_number = axis)
		ret = con.status()
		con.close()
		return ret

	'''
	@brief Prints the axis, position and velocity of the connected stages.
	'''
	def getStatus(self):
		xStatus = self.getStatusAxis(self.X_AXIS_SN)
		yStatus = self.getStatusAxis(self.Y_AXIS_SN)
		zStatus = self.getStatusAxis(self.Z_AXIS_SN)
		print("\nAxis:   Position [mm]:   Velocity [mm/s]:")
		print('-----   --------------   ----------------')
		print(("X       %6.3f          %6.3f" % (float(self.MAX_DIST) - xStatus.position, xStatus.velocity)))
		print(("Y       %6.3f          %6.3f" % (yStatus.position, yStatus.velocity)))
		print(("Z       %6.3f          %6.3f\n" % (float(self.MAX_DIST) - zStatus.position, zStatus.velocity)))

	'''
	@brief Provides the position of one or all axes.
	@param[in] axis String with the name of the axis we want to retrieve.
	@returns position[s] [X, Y, Z] of the stage.
	'''
	def getPos(self, axis = None):
		if (axis == 'X' or axis == 'x' or axis == None):
			with pyAPT.MTS50(serial_number = self.X_AXIS_SN) as con:
				status = con.status()
				posX = float(self.MAX_DIST_ENCODER - status.position_apt) / self.ENCODER_SCALE
			if (axis != None):
				return posX
		if (axis == 'Y' or axis == 'y' or axis == None):
			with pyAPT.MTS50(serial_number = self.Y_AXIS_SN) as con:
				status = con.status()
				posY = float(status.position_apt) / self.ENCODER_SCALE
			if (axis != None):
				return posY
		if (axis == 'Z' or axis == 'z' or axis == None):
			with pyAPT.MTS50(serial_number = self.Z_AXIS_SN) as con:
				status = con.status()
				posZ = float(self.MAX_DIST_ENCODER - status.position_apt) / self.ENCODER_SCALE
			if (axis != None):
				return posZ
		return [posX, posY, posZ]

	'''
	@brief Sends the 3D linear stage to the position (0, 0, 0).
	'''
	def goHome(self):
		# Move to home position of the stage
		self.moveAbsolute(self.MAX_DIST, 0, self.MAX_DIST)

		# Verify X axis home position
		con = pyAPT.MTS50(serial_number = self.X_AXIS_SN)
		con.home()
		con.close()
		
		# Verify Y axis home position
		con = pyAPT.MTS50(serial_number = self.Y_AXIS_SN)
		con.home()
		con.close()

		# Verify Z axis home position
		con = pyAPT.MTS50(serial_number = self.Z_AXIS_SN)
		con.home()
		con.close()

		# Move to our reference frame home position
		self.moveAbsolute(0, 0, 0)

	'''
	@brief This method performs a 3D raster scan.
	@param[in] step  Increment in microns from point to point.
	@param[in] delay Seconds of delay after each position has been reached.
	FIXME: show points in graph at the same time that the stage is moving.
	FIXME: rotate the 3D view so that it is equivalent to the real coordinate frame.
	'''
	def rasterScan(self, step, delay):
		# FIXME: reset plot if it was already opened
		# plt.close()

		# Going home to reset the encoders
		sys.stdout.write('Homing... ')
		sys.stdout.flush()
		self.moveAbsolute(0, 0, 0)
		print('OK')

		# Setting the initial direction of the X (k) and Y(j) axes
		kDir = self.RIGHT
		jDir = self.DOWN

		# Initialising iterators
		i = 0.0
		j = 0.0
		k = 0.0

		# Showing the window with the plot of the points
		# plt.show()

		# Looping through the workspace in a raster fashion
		while (i <= self.MAX_DIST):
			if j > self.MAX_DIST:
				j = self.MAX_DIST
				jDir = self.UP
			if j < 0:
				j = 0
				jDir = self.DOWN
			while (j >= 0 and j <= self.MAX_DIST):
				if k > self.MAX_DIST:
					k = self.MAX_DIST
					kDir = self.LEFT
				if k < 0:
					k = 0
					kDir = self.RIGHT
				while (k >= 0 and k <= self.MAX_DIST):
					self.moveAbsolute(k, j, i)
					print(('Current position: %6.3f %6.3f %6.3f' % (k, j, i)))
					# self.ax.scatter(k, j, i, zdir = 'z', c = 'red')
					# plt.draw()
					time.sleep(delay)
					print('Moving to next position ...')
					if kDir == self.RIGHT:
						k += step
					else:
						k -= step
				if jDir == self.DOWN:
					j += step
				else:
					j -= step
			i += step

	'''
	@brief Cylindrical scan starting from the floor and going up. For each height level it
	       performs (self.MAX_DIST / step) circles. The scanning is clockwise. The spacing
			 between the points of each circle is maintained the same regardless the distance
			 to the centre of the cylinder. That is, the external circles have more points
			 than the internal ones to maintain the same spacing.
	@param[in] stepAngle Initial angle of separation between points. It is a ratio of pi. 
	@param[in] step      Increment of the radius of the circle for each step of scanning.
	                     It is also used for the increment in the z axis. It is a ratio of
								the maximum distance.
	@param[in] delay     Delay in seconds after a position has been reached.
	FIXME: rotate the 3D view so that it is equivalent to the real coordinate frame.
	'''
	def cylindricalScan(self, stepAngle, step, delay):
		# Checking that the parameters are ratios
		if (stepAngle > 1 or step > 1):
			print('The step angle and the step must be lower than one because they are ratios.')

		IN = 0
		OUT = 1
		stepAngle *= pi
		initialStepAngle = stepAngle
		phi = pi
		step *= self.MAX_DIST
		r = step
		z = 0
		rDir = OUT
		epsilon = 0.001
		
		# FIXME: reset plot if it was already opened
		# plt.close()

		# Going home to reset the encoders
		sys.stdout.write('Homing... ')
		sys.stdout.flush()
		# self.moveAbsolute(0, 0, 0)
		print('OK')

		# Showing the window with the plot of the points
		plt.show()

		# Looping around all the points of the cylinder
		while (z <= self.MAX_DIST):
			if r > self.MAX_DIST / 2:
				stepAngle = (stepAngle * r) / (r - step)
				r -= step
				rDir = IN
			else:
				stepAngle = initialStepAngle
				r = step
				rDir = OUT
				x = self.MAX_DIST / 2
				y = self.MAX_DIST / 2
				self.moveAbsolute(x, y, z)
				print(('Current position: %6.3f %6.3f %6.3f' % (x, y, z)))
				self.ax.scatter(x, y, z, zdir = 'z', c = 'red')
				plt.draw()
				time.sleep(delay)
			while ((r > step or abs(r - step) < epsilon) and (r < self.MAX_DIST / 2 or abs(r - self.MAX_DIST / 2) < epsilon)):
				while (phi > -pi):
					x = r * cos(phi) + self.MAX_DIST / 2
					y = r * sin(phi) + self.MAX_DIST / 2
					self.moveAbsolute(x, y, z)
					print(('Current position: %6.3f %6.3f %6.3f' % (x, y, z)))
					self.ax.scatter(x, y, z, zdir = 'z', c = 'red')
					plt.draw()
					time.sleep(delay)
					phi -= stepAngle
				if (rDir == IN):
					if (abs(r - step) > epsilon):
						stepAngle = (stepAngle * r) / (r - step)
					r -= step
				else:
					stepAngle = (stepAngle * r) / (r + step)
					r += step	
				phi = pi
			if (rDir == IN):
				x = self.MAX_DIST / 2
				y = self.MAX_DIST / 2
				self.moveAbsolute(x, y, z)
				print(('Current position: %6.3f %6.3f %6.3f' % (x, y, z)))
				self.ax.scatter(x, y, z, zdir = 'z', c = 'red')
				plt.draw()
				time.sleep(delay)
			z += step

	'''
	@brief Moving X axis of the stage to the position x (mm)
	@param[in] x Goal position in mm.
	'''
	def moveAbsoluteX(self, x):
		x = float(self.MAX_DIST) - x
		con = pyAPT.MTS50(serial_number = self.X_AXIS_SN)
		con.goto(x, wait = False)
		stat = con.status()
		while stat.moving:
			time.sleep(0.01)
			stat = con.status()
		con.close()

	'''
	@brief Moving Y axis of the stage to the position y (mm)
	@param[in] y Goal position in mm.
	'''
	def moveAbsoluteY(self, y):
		con = pyAPT.MTS50(serial_number = self.Y_AXIS_SN)
		con.goto(y, wait = False)
		stat = con.status()
		while stat.moving:
			time.sleep(0.01)
			stat = con.status()
		con.close()

	'''
	@brief Moving Z axis of the stage to the position z (mm)
	@param[in] z Goal position in mm.
	'''
	def moveAbsoluteZ(self, z):
		z = float(self.MAX_DIST) - z
		con = pyAPT.MTS50(serial_number = self.Z_AXIS_SN)
		con.goto(z, wait = False)
		stat = con.status()
		while stat.moving:
			time.sleep(0.01)
			stat = con.status()
		con.close()

	'''
	@brief Move the stage to the position x, y, z.
	@param[in] x     Position of the x axis in mm.
	@param[in] y     Position of the y axis in mm.
	@param[in] z     Position of the z axis in mm.
	@param[in] delay Delay (in seconds) after each position has been reached.
	'''
	def moveAbsolute(self, x, y, z):
		#tx = threading.Thread(target = self.moveAbsoluteX(x))
		#ty = threading.Thread(target = self.moveAbsoluteY(y))
		#tz = threading.Thread(target = self.moveAbsoluteZ(z))
		#tx.daemon = True
		#ty.daemon = True
		#tz.daemon = True
		#tx.start()
		#ty.start()
		#tz.start()
		self.moveAbsoluteX(x)
		self.moveAbsoluteY(y)
		self.moveAbsoluteZ(z)

	'''
	@brief TODO
	@param[in] x TODO
	@param[in] y TODO
	@param[in] z TODO
	@param[in] delayMs TODO
	'''
	def moveRelative(self, x, y, z):
		return 0
