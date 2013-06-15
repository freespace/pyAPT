from controller import Controller

class MTS50(Controller):
  """
  A controller for a MTS50/M-Z8 stage.
  """
  def __init__(self,*args, **kwargs):
    super(MTS50Controller, self).__init__(*args, **kwargs)

    # http://www.thorlabs.co.uk/thorProduct.cfm?partNumber=MTS50/M-Z8
    self.max_velocity = 3
    self.max_acceleration = 4.5

    self.position_scale = 34304
    self.velocity_scale = 767367.49
    self.acceleration_scale = 261.93

    self.linear_range = (0,50)

