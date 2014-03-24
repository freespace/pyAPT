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

    # from private communication with thorlabs tech support:
    # steps per revolution: 48
    # gearbox ratio: 256
    # pitch: 0.5 mm
    # thus to advance 1 mm you need to turn 48*256*2 times
    self.position_scale = 48 * 256 * 2
    self.velocity_scale = 366511.111
    self.acceleration_scale = 1/0.006

    self.linear_range = (0,50)

