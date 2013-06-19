from controller import Controller

class MTS50(Controller):
  """
  A controller for a MTS50/M-Z8 stage.
  """
  def __init__(self,*args, **kwargs):
    super(MTS50, self).__init__(*args, **kwargs)

    # http://www.thorlabs.co.uk/thorProduct.cfm?partNumber=MTS50/M-Z8
    # Note that these values are pulled from the APT User software,
    # as they agree with the real limits of the stage better than
    # what the website or the user manual states
    self.max_velocity = 0.45
    self.max_acceleration = 0.45

    self.position_scale = 34304
    self.velocity_scale = 767367.49
    self.acceleration_scale = 261.93

    self.linear_range = (0,50)

