#!/usr/bin/env python
"""
Usage: python goto.py <serial> <position_mm>

This program tells the specified controller to move the stage to the specified
position.
"""

import time
import pylibftdi
import pyAPT

def main(args):
  if len(args)<3:
    print __doc__
    return 1
  else:
    serial = args[1]
    position = int(args[2])

  try:
    with pyAPT.Controller(serial_number=serial) as con:
      print 'Found APT controller S/N',serial
      print '\tMoving stage to %dmm...'%(position),
      con.goto(position)
      print 'moved'
      print '\tNew position: %dmm'%(con.position())
      return 0
  except pylibftdi.FtdiError as ex:
    print '\tCould not find APT controller S/N of',serial
    return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

