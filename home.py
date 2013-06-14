#!/usr/bin/env python

import time
import pylibftdi
import pyAPT


def main(args):
  print 'Looking for APT controllers'
  drv = pylibftdi.Driver()
  controllers = drv.list_devices()
  serial = args[1]

  if serial:
    controllers = filter(lambda x:x[2] == serail, controllers)

  if controllers:
    for con in controllers:
      print 'Found %s %s S/N: %s'%con
      with pyAPT.Controller(serial_number=con[2]) as con:
        print '\tIdentifying controller'
        con.identify()
        print '\tResetting controller parameters'
        con.reset_params()
        print '\tHoming parameters:', con.request_home_params()
        print '\tHoming stage...',
        con.home(velocity=1)
        print 'homed'

      return 0
  else:
    print '\tNo APT controllers found. Maybe you need to specify a PID'
    return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

