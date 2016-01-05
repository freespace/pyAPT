#!/usr/bin/env python
"""
Usage: python get_position.py [<serial>]

This program reads the position of all APT controllers found, or the one
specified
"""
from __future__ import absolute_import
from __future__ import print_function

import time
import pylibftdi
import pyAPT

def main(args):
  print('Looking for APT controllers')
  drv = pylibftdi.Driver()
  controllers = drv.list_devices()

  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    controllers = [x for x in controllers if x[2] == serial]

  if controllers:
    for con in controllers:
      print('Found %s %s S/N: %s'%con)
      with pyAPT.MTS50(serial_number=con[2]) as con:
        print('\tPosition (mm) = %.2f [enc:%d]'%(con.position(), con.position(raw=True)))

      return 0
  else:
    print('\tNo APT controllers found. Maybe you need to specify a PID')
    return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

