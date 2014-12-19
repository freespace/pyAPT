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

'''

import pyAPT
import threading
import time
from runner import runner_serial

class LinearStage(object):

	# Constants
	X_AXIS_SN        = '83853044'
	Y_AXIS_SN        = '83854474'
	Z_AXIS_SN        = '83853018'
	MAX_DIST         = 50         # microns
	ENCODER_SCALE    = 24576
	MAX_DIST_ENCODER = MAX_DIST * ENCODER_SCALE
	RIGHT = 0
	LEFT = 1
	DOWN = 0
	UP = 1
	
	'''
	@brief TODO
	'''
#	def __init__(self):
#		self.running = True
#		self.threads = []

	def getInfoAxis(self, axis):
		con = pyAPT.MTS50(serial_number = axis)
		return con.info()

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
			print("\t%12s: %s" % (labels[idx], bytes(ainfo)))
		print("\nInformation of the Y axis:")
		print('--------------------------')
		for idx, ainfo in enumerate(yInfo):
			print("\t%12s: %s" % (labels[idx], bytes(ainfo)))
		print("\nInformation of the Z axis:")
		print('--------------------------')
		for idx, ainfo in enumerate(zInfo):
			print("\t%12s: %s" % (labels[idx], bytes(ainfo)))
		print("\n")
	
	'''
	@brief Obtains the current position, velocity and status of a linear stage connected through USB.
	@param[in] axis Serial number of the target linear stage.
	@returns Status for the stage with the serial number provided.
	'''
	def getStatusAxis(self, axis):
		con = pyAPT.MTS50(serial_number = axis)
		return con.status()

	'''
	@brief Prints the axis, position and velocity of the connected stages.
	'''
	def getStatus(self):
		xStatus = self.getStatusAxis(self.X_AXIS_SN)
		yStatus = self.getStatusAxis(self.Y_AXIS_SN)
		zStatus = self.getStatusAxis(self.Z_AXIS_SN)
		print("\nAxis:   Position [mm]:   Velocity [mm/s]:")
		print('-----   --------------   ----------------')
		print("X       %6.3f          %6.3f" % (float(self.MAX_DIST) - xStatus.position, xStatus.velocity))
		print("Y       %6.3f          %6.3f" % (yStatus.position, yStatus.velocity))
		print("Z       %6.3f          %6.3f\n" % (float(self.MAX_DIST) - zStatus.position, zStatus.velocity))
		
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
		con = pyAPT.MTS50(serial_number = self.X_AXIS_SN)
		con.home(velocity = 40)
		con = pyAPT.MTS50(serial_number = self.Y_AXIS_SN)
		con.home(velocity = 40)
		con = pyAPT.MTS50(serial_number = self.Z_AXIS_SN)
		con.home(velocity = 40)
		self.moveAbsolute(0, 0, 0)

	'''
		@brief This method performs a 3D raster scan.
		@param[in] step    Increment in microns from point to point.
		@param[in] delayMs Time delay after each position has been reached. It stabilises the movement.
	'''
	def rasterScan(self, step, delayMs):
		# Going home to reset the encoders
		print('Homing... ')
		self.goHome()
		print("OK\n")

		# Setting the initial direction of the X (k) and Y(j) axes
		kDir = self.RIGHT
		jDir = self.DOWN		
		
		# Initialising iterators
		i = 0
		j = 0
		k = 0

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
					time.sleep(delayMs / 1000)
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
		@brief TODO
		@param[in] stepX TODO
		@param[in] stepY TODO
		@param[in] stepZ TODO
		@param[in] delayMs TODO
	'''
	def spiralScan(self, stepX, stepY, stepZ, delayMs):
		return 0

	'''
	TODO
	'''
	def moveAbsoluteX(self, x):
		x = float(self.MAX_DIST) - x
		con = pyAPT.MTS50(serial_number = self.X_AXIS_SN)
		con.goto(x, wait = False)
		stat = con.status()
		while stat.moving:
			out = '        pos %3.2fmm vel %3.2fmm/s'%(stat.position, stat.velocity)
			# sys.stdout.write(out)
			time.sleep(0.01)
			stat = con.status()
			l = len(out)
			# sys.stdout.write('\b'*l)
			# sys.stdout.write(' '*l)
			# sys.stdout.write('\b'*l)

	'''
	TODO
	'''
	def moveAbsoluteY(self, y):
		con = pyAPT.MTS50(serial_number = self.Y_AXIS_SN)
		con.goto(y, wait = False)
		stat = con.status()
		while stat.moving:
			out = '        pos %3.2fmm vel %3.2fmm/s'%(stat.position, stat.velocity)
			# sys.stdout.write(out)
			time.sleep(0.01)
			stat = con.status()
			l = len(out)
			# sys.stdout.write('\b'*l)
			# sys.stdout.write(' '*l)
			# sys.stdout.write('\b'*l)

	'''
	TODO
	'''
	def moveAbsoluteZ(self, z):
		z = float(self.MAX_DIST) - z
		con = pyAPT.MTS50(serial_number = self.Z_AXIS_SN)
		con.goto(z, wait = False)
		stat = con.status()
		while stat.moving:
			out = '        pos %3.2fmm vel %3.2fmm/s'%(stat.position, stat.velocity)
			# sys.stdout.write(out)
			time.sleep(0.01)
			stat = con.status()
			l = len(out)
			# sys.stdout.write('\b'*l)
			# sys.stdout.write(' '*l)
			# sys.stdout.write('\b'*l)

	'''
		@brief TODO
		@param[in] x TODO
		@param[in] y TODO
		@param[in] z TODO
		@param[in] delayMs TODO
	'''
	def moveAbsolute(self, x, y, z):
		tx = threading.Thread(target = self.moveAbsoluteX(x))
		ty = threading.Thread(target = self.moveAbsoluteY(y))
		tz = threading.Thread(target = self.moveAbsoluteZ(z))
		tx.daemon = True
		ty.daemon = True
		tz.daemon = True
		tx.start()
		ty.start()
		tz.start()

	'''
		@brief TODO
		@param[in] x TODO
		@param[in] y TODO
		@param[in] z TODO
		@param[in] delayMs TODO
	'''
	def moveRelative(self, x, y, z):
		return 0
