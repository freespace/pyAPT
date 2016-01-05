"""
Simple class which encapsulate an APT controller
"""
from __future__ import absolute_import, division
import pylibftdi
import time
import struct as st

from .message import Message
from . import message

class OutOfRangeError(Exception):
  def __init__(self, requested, allowed):
    val = '%f requested, but allowed range is %.2f..%.2f'%(requested, allowed[0], allowed[1])
    super(OutOfRangeError, self).__init__(val)

class Controller(object):
  def __init__(self, serial_number=None, label=None):
    super(Controller, self).__init__()

    if type(serial_number) == bytes:
      serial_number = serial_number.decode()
    else:
      serial_number = str(serial_number)

    # this takes up to 2-3s:
    dev = pylibftdi.Device(mode='b', device_id=serial_number)
    dev.baudrate = 115200

    def _checked_c(ret):
      if not ret == 0:
        raise Exception(dev.ftdi_fn.ftdi_get_error_string())

    _checked_c(dev.ftdi_fn.ftdi_set_line_property(  8,   # number of bits
                                                    1,   # number of stop bits
                                                    0   # no parity
                                                    ))
    time.sleep(50.0/1000)

    dev.flush(pylibftdi.FLUSH_BOTH)

    time.sleep(50.0/1000)

    # skipping reset part since it looks like pylibftdi does it already

    # this is pulled from ftdi.h
    SIO_RTS_CTS_HS = (0x1 << 8)
    _checked_c(dev.ftdi_fn.ftdi_setflowctrl(SIO_RTS_CTS_HS))

    _checked_c(dev.ftdi_fn.ftdi_setrts(1))

    self.serial_number = serial_number
    self.label = label
    self._device = dev

    # some conservative limits
    # velocity is in mm/s
    # acceleration is in mm^2/s
    self.max_velocity = 0.3
    self.max_acceleration = 0.3

    # these define how encode count translates into position, velocity
    # and acceleration. e.g. 1 mm is equal to 1 * self.position_scale

    # these are set to None on purpose - you should never use this class
    # as is.
    self.position_scale = None
    self.velocity_scale = None
    self.acceleration_scale = None

    # defines the linear, i.e. distance, range of the controller
    # unit is in mm
    self.linear_range = (0,50)

    # whether or not sofware limit in position is applied
    self.soft_limits = True

    # the message queue are messages that are sent asynchronously. For example
    # if we performed a move, and are waiting for move completed message,
    # any other message received in the mean time are place in the queue.
    self.message_queue = []

  def __enter__(self):
    return self

  def __exit__(self, type_, value, traceback):
    self.close()

  def __del__(self):
    self.close()

  def close(self):
    if not self._device.closed:
      # print 'Closing connnection to controller',self.serial_number
      self.stop(wait=False)
      # XXX we might want a timeout here, or this will block forever
      self._device.close()

  def _send_message(self, m):
    """
    m should be an instance of Message, or has a pack() method which returns
    bytes to be sent to the controller
    """
    self._device.write(m.pack())

  def _read(self, length, block=True):
    """
    If block is True, then we will return only when have have length number of
    bytes. Otherwise we will perform a read, then immediately return with
    however many bytes we managed to read.

    Note that if no data is available, then an empty byte string will be
    returned.
    """
    data = bytes()
    while len(data) < length:
      diff = length - len(data)
      data += self._device.read(diff)
      if not block:
        break

      time.sleep(0.001)

    return data

  def _read_message(self):
    data = self._read(message.MGMSG_HEADER_SIZE)
    msg = Message.unpack(data, header_only=True)
    if msg.hasdata:
      data = self._read(msg.datalength)
      msglist = list(msg)
      msglist[-1] = data
      return Message._make(msglist)
    return msg

  def _wait_message(self, expected_messageID):
    found = False
    while not found:
      m = self._read_message()
      found = m.messageID == expected_messageID
      if found:
        return m
      else:
        self.message_queue.append(m)

  def _position_in_range(self, absolute_pos_mm):
    """
    Returns True if requested absolute position is within range, False
    otherwise
    """
    # get rid of floating point artifacts below our resolution
    enccnt = int(absolute_pos_mm * self.position_scale)
    absolute_pos_mm = enccnt / self.position_scale

    if absolute_pos_mm < self.linear_range[0]:
      return False

    if absolute_pos_mm > self.linear_range[1]:
      return False

    return True

  def status(self, channel=1):
    """
    Returns the status of the controller, which is its position, velocity, and
    statusbits

    Position and velocity will be in mm and mm/s respectively.
    """
    reqmsg = Message(message.MGMSG_MOT_REQ_DCSTATUSUPDATE, param1=channel)
    self._send_message(reqmsg)

    getmsg = self._wait_message(message.MGMSG_MOT_GET_DCSTATUSUPDATE)
    return ControllerStatus(self, getmsg.datastring)

  def identify(self):
    """
    Flashes the controller's activity LED
    """
    idmsg = Message(message.MGMSG_MOD_IDENTIFY)
    self._send_message(idmsg)

  def reset_parameters(self):
    """
    Resets all parameters to their EEPROM default values.

    IMPORTANT: only one class of controller appear to support this at the
    moment, that being the BPC30x series.
    """
    resetmsg = Message(message.MGMSG_MOT_SET_PZSTAGEPARAMDEFAULTS)
    self._send_message(resetmsg)

  def request_home_params(self):
    reqmsg = Message(message.MGMSG_MOT_REQ_HOMEPARAMS)
    self._send_message(reqmsg)

    getmsg = self._wait_message(message.MGMSG_MOT_GET_HOMEPARAMS)
    dstr = getmsg.datastring

    """
    <: little endian
    H: 2 bytes for channel id
    H: 2 bytes for home direction
    H: 2 bytes for limit switch
    i: 4 bytes for homing velocity
    i: 4 bytes for offset distance
    """
    return st.unpack('<HHHii', dstr)

  def suspend_end_of_move_messages(self):
      suspendmsg = Message(message.MGMSG_MOT_SUSPEND_ENDOFMOVEMSGS)
      self._send_message(suspendmsg)

  def resume_end_of_move_messages(self):
      resumemsg = Message(message.MGMSG_MOT_RESUME_ENDOFMOVEMSGS)
      self._send_message(resumemsg)

  def home(self, wait=True, velocity=None, offset=0):
    """
    When velocity is not None, homing parameters will be set so homing velocity
    will be as given, in mm per second.

    offset is the home offset in mm, which will be converted to APT units and
    passed to the controller.

    When wait is true, this method doesn't return until MGMSG_MOT_MOVE_HOMED
    is received. Otherwise it returns immediately after having sent the
    message.

    This method returns an instance of ControllerStatus if wait is True, None
    otherwise.
    """

    # first get the current settings for homing. We do this because despite
    # the fact that the protocol spec says home direction, limit switch,
    # and offset distance parameters are not used, they are in fact 
    # significant. If I just pass in 0s for those parameters when setting
    # homing parameter the stage goes the wrong way and runs itself into
    # the other end, causing an error condition.
    #
    # To get around this, and the fact the correct values don't seem to be
    # documented, we get the current parameters, assuming they are correct,
    # and then modify only the velocity and offset component, then send it 
    # back to the controller.
    curparams = list(self.request_home_params())

    # make sure we never exceed the limits of our stage

    offset = min(offset, self.linear_range[1])
    offset = max(offset, 0)
    offset_apt = offset * self.position_scale

    """
    <: little endian
    H: 2 bytes for channel id
    H: 2 bytes for home direction
    H: 2 bytes for limit switch
    i: 4 bytes for homing velocity
    i: 4 bytes for offset distance
    """

    if velocity:
      velocity = min(velocity, self.max_velocity)
      curparams[-2] = int(velocity * self.velocity_scale)

    curparams[-1] = offset_apt

    newparams= st.pack( '<HHHii',*curparams)

    homeparamsmsg = Message(message.MGMSG_MOT_SET_HOMEPARAMS, data=newparams)
    self._send_message(homeparamsmsg)

    if wait:
      self.resume_end_of_move_messages()
    else:
      self.suspend_end_of_move_messages()

    homemsg = Message(message.MGMSG_MOT_MOVE_HOME)
    self._send_message(homemsg)

    if wait:
      self._wait_message(message.MGMSG_MOT_MOVE_HOMED)
      return self.status()

  def position(self, channel=1, raw=False):
    reqmsg = Message(message.MGMSG_MOT_REQ_POSCOUNTER, param1=channel)
    self._send_message(reqmsg)

    getmsg = self._wait_message(message.MGMSG_MOT_GET_POSCOUNTER)
    dstr = getmsg.datastring

    """
    <: little endian
    H: 2 bytes for channel id
    i: 4 bytes for position
    """
    chanid,pos_apt=st.unpack('<Hi', dstr)

    if not raw:
      # convert position from POS_apt to POS using _position_scale
      return 1.0*pos_apt / self.position_scale
    else:
      return pos_apt

  def goto(self, abs_pos_mm, channel=1, wait=True):
    """
    Tells the stage to goto the specified absolute position, in mm.

    abs_pos_mm will be clamped to self.linear_range

    When wait is True, this method only returns when the stage has signaled
    that it has finished moving.

    Note that the wait is implemented by waiting for MGMSG_MOT_MOVE_COMPLETED,
    then querying status until the position returned matches the requested
    position, and velocity is zero

    This method returns an instance of ControllerStatus if wait is True, None
    otherwise.

    If the requested position is beyond the limits defined in
    self.linear_range, and OutOfRangeError will be thrown.
    """

    if self.soft_limits and not self._position_in_range(abs_pos_mm):
      raise OutOfRangeError(abs_pos_mm, self.linear_range)

    abs_pos_apt = int(abs_pos_mm * self.position_scale)

    """
    <: little endian
    H: 2 bytes for channel id
    i: 4 bytes for absolute position
    """
    params = st.pack( '<Hi', channel, abs_pos_apt)

    if wait:
      self.resume_end_of_move_messages()
    else:
      self.suspend_end_of_move_messages()

    movemsg = Message(message.MGMSG_MOT_MOVE_ABSOLUTE,data=params)
    self._send_message(movemsg)

    if wait:
      msg = self._wait_message(message.MGMSG_MOT_MOVE_COMPLETED)
      sts = ControllerStatus(self, msg.datastring)
      # I find sometimes that after the move completed message there is still
      # some jittering. This aims to wait out the jittering so we are
      # stationary when we return
      while sts.velocity_apt:
        time.sleep(0.01)
        sts = self.status()
      return sts
    else:
      return None

  def move(self, dist_mm, channel=1, wait=True):
    """
    Tells the stage to move from its current position the specified
    distance, in mm

    This is currently implemented by getting the current position, then
    computing a new absolute position using dist_mm, then calls
    goto() and returns it returns. Check documentation for goto() for return
    values and such.
    """
    curpos = self.position()
    newpos = curpos + dist_mm

    # We could implement MGMSG_MOT_MOVE_RELATIVE, or we can use goto again
    # because we calculate the new absolute position anyway.
    #
    # The advantage of implementing MGMSG_MOT_MOVE_RELATIVE is that things
    # will be a little faster, because we don't need to get the current
    # position first. The advantage of reusing self.goto is that it is easier
    # to implement initially.
    #
    # Of course by the time I have finished writing this comment, I could have
    # just implemented MGMSG_MOT_MOVE_RELATIVE.
    return self.goto(newpos, channel=channel, wait=wait)

  def set_soft_limits(self, soft_limits):
    """
    Sets whether range limits are observed in software.
    """
    self.soft_limits = soft_limits

  def set_velocity_parameters(self, acceleration=None, max_velocity=None, channel=1):
    """
    Sets the trapezoidal velocity parameters of the controller. Note that
    minimum velocity cannot be set, because protocol demands it is always
    zero.

    When called without arguments, max acceleration and max velocity will
    be set to self.max_acceleration and self.max_velocity
    """
    if acceleration == None:
      acceleration = self.max_acceleration

    if max_velocity == None:
      max_velocity = self.max_velocity

    # software limiting again for extra safety
    acceleration = min(acceleration, self.max_acceleration)
    max_velocity = min(max_velocity, self.max_velocity)

    acc_apt = acceleration * self.acceleration_scale
    max_vel_apt = max_velocity * self.velocity_scale

    """
    <: small endian
    H: 2 bytes for channel
    i: 4 bytes for min velocity
    i: 4 bytes for acceleration
    i: 4 bytes for max velocity
    """
    params = st.pack('<Hiii',channel,0,acc_apt, max_vel_apt)
    setmsg = Message(message.MGMSG_MOT_SET_VELPARAMS, data=params)
    self._send_message(setmsg)

  def velocity_parameters(self, channel=1, raw=False):
    """
    Returns the trapezoidal velocity parameters of the controller, that is
    minimum start velocity, acceleration, and maximum velocity. All of which
    are returned in realworld units.

    channel specifies the channel to query.

    raw specifies whether the raw controller values are returned, or the scaled
    real world values. Defaults to False.

    Example:
      min_vel, acc, max_vel = con.velocity_parameters()
    """
    reqmsg = Message(message.MGMSG_MOT_REQ_VELPARAMS, param1=channel)
    self._send_message(reqmsg)

    getmsg = self._wait_message(message.MGMSG_MOT_GET_VELPARAMS)

    """
    <: small endian
    H: 2 bytes for channel
    i: 4 bytes for min velocity
    i: 4 bytes for acceleration
    i: 4 bytes for max velocity
    """
    ch,min_vel,acc,max_vel = st.unpack('<Hiii',getmsg.datastring)

    if not raw:
      min_vel /= self.velocity_scale
      max_vel /= self.velocity_scale
      acc /= self.acceleration_scale

    return min_vel, acc, max_vel

  def info(self):
    """
    Gets hardware info of the controller, returned as a tuple containing:
      - serial number
      - model number
      - hardware type, either 45 for multi-channel motherboard, or 44 for
        brushless DC motor
      - firmware version as major.interim.minor
      - notes
      - hardware version number
      - modification state of controller
      - number of channels
    """

    reqmsg = Message(message.MGMSG_HW_REQ_INFO)
    self._send_message(reqmsg)

    getmsg = self._wait_message(message.MGMSG_HW_GET_INFO)
    """
    <: small endian
    I:    4 bytes for serial number
    8s:   8 bytes for model number
    H:    2 bytes for hw type
    4s:   4 bytes for firmware version
    48s:  48 bytes for notes
    12s:  12 bytes of empty space
    H:    2 bytes for hw version
    H:    2 bytes for modificiation state
    H:    2 bytes for number of channels
    """
    info = st.unpack('<I8sH4s48s12sHHH', getmsg.datastring)

    sn,model,hwtype,fwver,notes,_,hwver,modstate,numchan = info

    fwverminor = ord(fwver[0])
    fwverinterim = ord(fwver[1])
    fwvermajor = ord(fwver[2])

    fwver = '%d.%d.%d'%(fwvermajor,fwverinterim, fwverminor)

    return (sn,model,hwtype,fwver,notes,hwver,modstate,numchan)

  def stop(self, channel=1, immediate=False, wait=True):
    """
    Stops the motor on the specified channel. If immediate is True, then the
    motor stops immediately, otherwise it stops in a profiled manner, i.e.
    decelerates accoding to max acceleration from current velocity down to zero

    If wait is True, then this method returns only when MGMSG_MOT_MOVE_STOPPED
    is read, and controller reports velocity of 0.

    This method returns an instance of ControllerStatus if wait is True, None
    otherwise.
    """

    if wait:
      self.resume_end_of_move_messages()
    else:
      self.suspend_end_of_move_messages()

    stopmsg = Message(message.MGMSG_MOT_MOVE_STOP,
                      param1=channel,
                      param2=int(immediate))
    self._send_message(stopmsg)

    if wait:
      self._wait_message(message.MGMSG_MOT_MOVE_STOPPED)
      sts = self.status()
      while sts.velocity_apt:
        time.sleep(0.001)
        sts = self.status()
      return sts
    else:
      return None

  def keepalive(self):
    """
    This sends MGMSG_MOT_ACK_DCSTATUSUPDATE to the controller to keep it
    from going dark.

    Per documentation:
      If using the USB port, this message called "server alive" must be sent
      by the server to the controller at least once a second or the controller
      will stop responding after ~50 commands
    """
    msg = Message(message.MGMSG_MOT_ACK_DCSTATUSUPDATE)
    self._send_message(msg)

  def __repr__(self):
    return 'Controller(serial=%s, device=%s)'%(self.serial_number, self._device)

class ControllerStatus(object):
  """
  This class encapsulate the controller status, which includes its position,
  velocity, and various flags.

  The position and velocity properties will return realworld values of 
  mm and mm/s respectively.
  """
  def __init__(self, controller, statusbytestring):
    """
    Construct an instance of ControllerStatus from the 14 byte status sent by
    the controller which contains the current position encoder count, the
    actual velocity, scaled, and statusbits.
    """

    super(ControllerStatus, self).__init__()

    """
    <: little endian
    H: 2 bytes for channel ID
    i: 4 bytes for position counter
    h: 2 bytes for velocity
    H: 2 bytes reserved
    I: 4 bytes for status

    Note that velocity in the docs is stated as a unsigned word, by in reality
    it looks like it is signed.
    """
    channel, pos_apt, vel_apt, _, statusbits = st.unpack( '<HihHI',
                                                          statusbytestring)

    self.channel = channel
    if pos_apt:
      self.position = float(pos_apt) / controller.position_scale
    else:
      self.position = 0

    # XXX the protocol document, revision 7, is explicit about the scaling
    # Note that I don't trust this value, because the measured velocity
    # does not correspond to the value from the scaling. The value used here
    # is derived from trial and error
    if vel_apt:
      self.velocity = float(vel_apt) / 10
    else:
      self.velocity = 0

    self.statusbits = statusbits

    # save the "raw" controller values since they are convenient for
    # zero-checking
    self.position_apt = pos_apt
    self.position_scale = controller.position_scale
    self.velocity_apt = vel_apt

  @property
  def forward_hardware_limit_switch_active(self):
    return self.statusbits & 0x01

  @property
  def reverse_hardware_limit_switch_active(self):
    return self.statusbits & 0x02

  @property
  def moving(self):
    return self.moving_forward or self.moving_reverse
  @property
  def moving_forward(self):
    return self.statusbits & 0x10

  @property
  def moving_reverse(self):
    return self.statusbits & 0x20

  @property
  def jogging_forward(self):
    return self.statusbits & 0x40

  @property
  def jogging_reverse(self):
    return self.statusbits & 0x80

  @property
  def homing(self):
    return self.statusbits & 0x200

  @property
  def homed(self):
    return self.statusbits & 0x400

  @property
  def tracking(self):
    return self.statusbits & 0x1000

  @property
  def settled(self):
    return self.statusbits & 0x2000

  @property
  def excessive_position_error(self):
    """
    This flag means that there is excessive positioning error, and
    the stage should be re-homed. This happens if while moving the stage
    is impeded, and where it thinks it is isn't where it is
    """
    return self.statusbits & 0x4000

  @property
  def motor_current_limit_reached(self):
    return self.statusbits & 0x01000000

  @property
  def channel_enabled(self):
    return self.statusbits & 0x80000000


  @property
  def shortstatus(self):
    """
    Returns a short, fixed width, status line that shows whether the
    controller is moving, the direction, whether it has been homed, and
    whether excessive position error is present.

    These are shown via the following letters:
      H: homed

      M: moving
      T: tracking
      S: settled

      F: forward limit switch tripped
      R: reverse limit switch tripped
      E: excessive position error

    Format of the string is as follows:
      H MTS FRE

    Each letter may or may not be present.  When a letter is present, it is a
    positive indication of the condition.

    e.g.

    "H M-- ---" means homed, moving
    "H M-- --E" means homed, moving reverse, excessive position error
    """
    shortstat = []
    def add(flag, letter):
      if flag:
        shortstat.append(letter)
      else:
        shortstat.append('-')

    sep = ' '
    add(self.homed, 'H')

    shortstat.append(sep)

    add(self.moving, 'M')
    add(self.tracking, 'T')
    add(self.settled, 'S')

    shortstat.append(sep)

    add(self.forward_hardware_limit_switch_active, 'F')
    add(self.reverse_hardware_limit_switch_active, 'R')
    add(self.excessive_position_error, 'E')

    return ''.join(shortstat)

  def flag_strings(self):
    """
    Returns the various flags as user readable strings
    """
    """
    XXX Breaking the DRY principle here, but this is so much more compact!
    """
    masks={ 0x01:       'Forward hardware limit switch active',
            0x02:       'Reverse hardware limit switch active',
            0x10:       'In motion, moving forward',
            0x20:       'In motion, moving backward',
            0x40:       'In motion, jogging forward',
            0x80:       'In motion, jogging backward',
            0x200:      'In motion, homing',
            0x400:      'Homed',
            0x1000:     'Tracking',
            0x2000:     'Settled',
            0x4000:     'Excessive position error',
            0x01000000: 'Motor current limit reached',
            0x80000000: 'Channel enabled'
            }
    statuslist = []
    for bitmask in masks:
      if self.statusbits & bitmask:
        statuslist.append(masks[bitmask])

    return statuslist

  def __str__(self):
    return 'pos=%.2fmm vel=%.2fmm/s, flags=%s'%(self.position, self.velocity, self.flag_strings())

