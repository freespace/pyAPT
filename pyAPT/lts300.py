from __future__ import absolute_import, division
from .controller import Controller

class LTS300(Controller):
  """
  A controller for a LTS300 stage.
  """
  def __init__(self,*args, **kwargs):
    super(LTS300, self).__init__(*args, **kwargs)

    # http://www.thorlabs.co.uk/thorProduct.cfm?partNumber=LTS300
    
    # Values from APT Communications Protocol Rev 16
    # https://www.thorlabs.de/Software/Motion%20Control%5CAPT_Communications_Protocol_Rev_16.pdf

    self.max_velocity = 5.0
    self.max_acceleration = 5.0

    # The BSC20x series and MST602 stepper controllers include a Trinamics encoder with a 
    # resolution of 2048 microsteps per full step, giving 409600 micro-steps per revolution
    # for a 200 step motor. 

    # Values below are Trinamic converted values for position(us), velocity(us/s) and
    # acceleration (us/sec^2)

    self.position_scale = 409600
    self.velocity_scale = 21987328
    self.acceleration_scale = 4506

    # The linear range for this stage is 300mm
    self.linear_range = (0,300)

