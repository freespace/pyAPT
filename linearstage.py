'''
	@brief Class that represents a Thorlabs 3D linear stage.
	       It allows the user to perform different types of scans throught
			 the workspace.
	@author Luis Carlos Garcia-Peraza Herrera <luis.herrera.14@ucl.ac.uk>
	@author Efthymios Maneas <efthymios.maneas.14@ucl.ac.uk>
'''

from get_info import *

class LinearStage:

	'''
		@brief TODO
	'''
	def getInfo(self):
		info()
	'''
		@brief TODO
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
		@brief TODO
		@param[in] x TODO
		@param[in] y TODO
		@param[in] z TODO
		@param[in] delayMs TODO
	'''
	def moveAbsolute(self, x, y, z):
		return 0

	'''
		@brief TODO
		@param[in] x TODO
		@param[in] y TODO
		@param[in] z TODO
		@param[in] delayMs TODO
	'''
	def moveRelative(self, x, y, z):
		return 0

	# Attributes
	posX = -1;
	posY = -1;
	posZ = -1;
