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

    # yeah so manual values are junk. APT User seems to have the correct
    # values built in, in that when I tell it to go 5mm, it goes 5mm. So to
    # compute these values:
    #   1. In APT User set a distance, max velocity, and max accel in move
    #      sequencer
    #   2. Home and run
    #   3. Extra the 'raw' values from the controller using pyAPT
    #   4. Compute scaling factors

    self.position_scale = 24576.059
    self.velocity_scale = 366511.111
    self.acceleration_scale = 1/0.006

    self.linear_range = (0,50)

