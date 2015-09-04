from __future__ import absolute_import, division
from .controller import Controller

class PRM1(Controller):
  """
  A controller for a PRM1 rotation stage
  """
  def __init__(self,*args, **kwargs):
    super(PRM1, self).__init__(*args, **kwargs)

    # http://www.thorlabs.de/newgrouppage9.cfm?objectgroup_id=2875
    # Note that these values should be pulled from the APT User software,
    # as they agree with the real limits of the stage better than
    # what the website or the user manual states
    self.max_velocity = 0.3 # units?
    self.max_acceleration = 0.3 # units?

    # from the manual
    # encoder counts per revoultion of the output shaft: 34304
    # no load speed: 16500 rpm = 275 1/s
    # max rotation velocity: 25deg/s
    # Gear ratio: 274 / 25 rounds/deg
    # to move 1 deg: 274/25 rounds = 274/25 * 34304 encoder steps
    # measured value: 1919.2689
    # There is an offset off 88.2deg -> enc(0) = 88.2deg
    enccnt = 1919.2698

    T = 2048/6e6

    # these equations are taken from the APT protocol manual
    self.position_scale = enccnt  #the number of enccounts per deg
    self.velocity_scale = enccnt * T * 65536
    self.acceleration_scale = enccnt * T * T * 65536

    self.linear_range = (-180,180)

