#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
import pyAPT

from runner import runner_serial

@runner_serial
def status(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    status = con.status()
    print '\tController status:'
    print '\t\tPosition: %.2fmm'%(status.position)
    print '\t\tVelocity: %.2fmm'%(status.velocity)
    print '\t\tStatus:',status.flag_strings()


if __name__ == '__main__':
  import sys
  sys.exit(status())

