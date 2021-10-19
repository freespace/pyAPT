from __future__ import absolute_import, division
from .controller import Controller

class KDC101(Controller):
  """
  A controller for a KDC101 linear translation stage.
  """
  def __init__(self,*args, **kwargs):
    super(KDC101, self).__init__(*args, **kwargs)

    # can be set manually in the menu of the KDC101 
    self.max_velocity = 0.48
    self.max_acceleration = 0.48

    # see manual https://www.thorlabs.com/drawings/7edd686f3ac5c5ad-097D682C-AA42-53E4-3C7EB522A4840171/KDC101-KDC101ManualforAPT.pdf
    enccnt = 34304 
    T = 2048/6e6

    # these equations are taken from the APT protocol manual
    self.position_scale = enccnt
    self.velocity_scale = enccnt * T * 65536
    self.acceleration_scale = enccnt * T * T * 65536

    self.linear_range = (0,50)

