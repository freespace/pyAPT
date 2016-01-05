#!/usr/bin/env python
"""
Usage: python goto.py <serial> <position_mm>

This program tells the specified controller to move the stage to the specified
position.
"""
from __future__ import absolute_import
from __future__ import print_function

import time
import pylibftdi
import pyAPT
import sys

def main(args):
  if len(args)<3:
    print(__doc__)
    return 1
  else:
    serial = args[1]
    position = float(args[2])

  try:
    with pyAPT.MTS50(serial_number=serial) as con:
      print('Found APT controller S/N',serial)
      print('\tMoving stage to %.2fmm...'%(position))
      st=time.time()
      con.goto(position, wait=False)
      stat = con.status()
      while stat.moving:
        out = '        pos %3.2fmm vel %3.2fmm/s'%(stat.position, stat.velocity)
        sys.stdout.write(out)
        time.sleep(0.01)
        stat=con.status()
        l = len(out)
        sys.stdout.write('\b'*l)
        sys.stdout.write(' '*l)
        sys.stdout.write('\b'*l)

      print('\tMove completed in %.2fs'%(time.time()-st))
      print('\tNew position: %.2fmm'%(con.position()))
      print('\tStatus:',con.status())
      return 0
  except pylibftdi.FtdiError as ex:
    print('\tCould not find APT controller S/N of',serial)
    return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

