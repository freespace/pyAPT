#!/usr/bin/env python
"""
Usage: python home.py [<serial>]

This program homes all APT controllers found, or of the one specified
"""

import time
import pylibftdi
import pyAPT

def home(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    print '\tIdentifying controller'
    con.identify()
    print '\tHoming parameters:', con.request_home_params()
    print '\tHoming stage...',
    con.home()
    print 'homed'

def main(args):
  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    home(serial)
    return 0
  else:
    print 'Looking for APT controllers'
    drv = pylibftdi.Driver()
    controllers = drv.list_devices()

    if controllers:
      for con in controllers:
        print 'Found %s %s S/N: %s'%con
        home(con[2])

      return 0
    else:
      print '\tNo APT controllers found. Maybe you need to specify a PID'
      return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

