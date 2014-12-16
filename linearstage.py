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
from get_info import *
from get_status import *
from runner import runner_serial

class LinearStage(object):

	# Constants
	X_AXIS_SN        = '83853044'; 
	Y_AXIS_SN        = '83854474';
	Z_AXIS_SN        = '83853018';
	MAX_DIST         = 50; # 50 mm
	ENCODER_SCALE    = 24576;
	MAX_DIST_ENCODER = MAX_DIST * ENCODER_SCALE;

	def __init__(self):
		self.running = True
		self.threads = []

	'''
	@brief Prints the serial number, model, type, firmware version and servo of all the connected stages.
	'''
	def getInfo(self):
		info()

	'''
	@brief Prints serial number, position and velocity of the connected stages.
	'''
	def getStatus(self):
		status()

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
		return 0

	'''
		@brief TODO
		@param[in] step TODO
		@param[in] delayMs TODO
	'''
	def quickRasterScan(self, step, delayMs):
		return 0

	'''
		@brief TODO
		@param[in] stepX TODO
		@param[in] stepY TODO
		@param[in] stepZ TODO
		@param[in] delayMs TODO
	'''
	def quickRasterScan(self, stepX, stepY, stepZ, delayMs):
		return 0
	
	'''
		@brief TODO
		@param[in] step TODO
		@param[in] delayMs TODO
	'''
	def rasterScan(self, step, delayMs):
		return 0

	'''
		@brief TODO
		@param[in] stepX TODO
		@param[in] stepY TODO
		@param[in] stepZ TODO
		@param[in] delayMs TODO
	'''
	def rasterScan(self, stepX, stepY, stepZ, delayMs):
		return 0

	'''
		@brief TODO
		@param[in] step TODO
		@param[in] delayMs TODO
	'''
	def spiralScan(self, step, delayMs):
		return 0

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
		with pyAPT.MTS50(serial_number = self.X_AXIS_SN) as con:
			con.goto(x)

	'''
	TODO
	'''
	def moveAbsoluteY(self, y):
		with pyAPT.MTS50(serial_number = self.Y_AXIS_SN) as con:
			con.goto(y)

	'''
	TODO
	'''
	def moveAbsoluteZ(self, z):
		z = float(self.MAX_DIST) - z
		with pyAPT.MTS50(serial_number = self.Z_AXIS_SN) as con:
			con.goto(z)

	'''
		@brief TODO
		@param[in] x TODO
		@param[in] y TODO
		@param[in] z TODO
		@param[in] delayMs TODO
	'''
	def moveAbsolute(self, x, y, z):
		tx = threading.Thread(target = self.moveAbsoluteX(x))
		print("hello")
		ty = threading.Thread(target = self.moveAbsoluteY(y))
		print("hello2")
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
