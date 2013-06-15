#!/usr/bin/env python
"""
Usage: python reset.py [<serial>]

Resets all controller parameters to their default EEPROM value.
"""
import pylibftdi
import pyAPT

def reset(serial):
    with pyAPT.Controller(serial_number=serial) as con:
      print '\tResetting controller parameters to EEPROM defaults'
      con.reset_parameters()

def main(args):
  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    reset(serial)
    return 0
  else:
    print 'Looking for APT controllers'
    drv = pylibftdi.Driver()
    controllers = drv.list_devices()

    if controllers:
      for con in controllers:
        print 'Found %s %s S/N: %s'%con
        reset(con[2])

      return 0
    else:
      print '\tNo APT controllers found. Maybe you need to specify a PID'
      return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

