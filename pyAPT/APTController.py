"""
Simple class which encapsulate an APT controller
"""
import pylibftdi
import time

class APTController(object):
  def __init__(self, serial_number=None, label=None):
    super(object, self).__init__()

    dev = pylibftdi.Device(mode='b', device_id=serial_number)
    dev.baudrate = 115200
    dev.ftdi_fn.ftdi_set_line_property( 8,   # number of bits
                                        1,   # number of stop bits
                                        0   # no parity
                                        )
    time.sleep(50.0/1000)

    dev.flush(pylibftdi.FLUSH_BOTH)

    time.sleep(50.0/1000)

    # skipping reset part since it looks like pylibftdi does it already

    # this is pulled from ftdi.h
    SIO_RTS_CTS_HS = (0x1 << 8)
    dev.ftdi_fn.ftdi_setflowctrl(SIO_RTS_CTS_HS)

    dev.ftdi_fn.ftdi_setrts(1)

    self.serial_number = serial_number
    self.label = label
    self._device = dev

  def __enter__(self):
    return self

  def __exit__(self, type_, value, traceback):
    self._device.close()

  def identify(self):
    """
    Flashes the controller's activity LED
    """
    idmsg = APTMessage.Message(APTMessage.MGMSG_MOD_IDENTIFY)
    self._device.write(idmsg.pack())

