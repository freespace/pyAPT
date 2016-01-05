#!/usr/bin/env python

"""
Usage: python bench.py

Performs simply benchmarks on how long it takes to list devices, open a device
and performing a status query
"""
from __future__ import absolute_import
from __future__ import print_function

import pylibftdi
import pyAPT
import time

def main(args):
  print('Looking for APT controllers')
  drv = pylibftdi.Driver()

  st = time.time()
  controllers = drv.list_devices()
  print('\tlist_devices:',time.time()-st)

  if controllers:
    for con in controllers:
      print('Found %s %s S/N: %s'%con)
      st = time.time()
      with pyAPT.MTS50(serial_number=con[2]) as con:
        print('\topen:',time.time()-st)
        st = time.time()
        status = con.status()
        print('\tstatus:',time.time()-st)

        print('\tController status:')
        print('\t\tPosition: %.2fmm'%(status.position))
        print('\t\tVelocity: %.2fmm'%(status.velocity))
        print('\t\tStatus:',status.flag_strings())

      return 0
  else:
    print('\tNo APT controllers found. Maybe you need to specify a PID')
    return 1


if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))
