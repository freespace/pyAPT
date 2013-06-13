#!/usr/bin/env python

import time
import pylibftdi
import APTMessage

pylibftdi.USB_PID_LIST+=[0xfaf0]

def main(args):
  identify_message = APTMessage.Message(APTMessage.MGMSG_MOD_IDENTIFY)

  print 'Looking for APT controllers'
  drv = pylibftdi.Driver()
  controllers = drv.list_devices()

  for con in controllers:
    print '\tIdentifying %s %s S/N: %s'%con
    dev = pylibftdi.Device(mode='b', device_id=con[2])

    # this is copied from APT_Communications_Protocol_Rev_7.pdf
    # See D2XXPG21.pdf for how to translate between D2XX API calls mentioned
    # in the protocol ref to libftdi calls

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

    dev.write(identify_message.pack())
    dev.close()

  dev = pylibftdi.Device()

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

