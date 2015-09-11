#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
from __future__ import absolute_import
from __future__ import print_function
import pyAPT

from runner import runner_serial

@runner_serial
def status(serial):
  with pyAPT.MTS50(serial_number=serial) as con:
    status = con.status()
    print('\tController status:')
    print('\t\tPosition: %.3fmm (%d cnt)'%(status.position, status.position_apt))
    print('\t\tVelocity: %.3fmm'%(status.velocity))
    print('\t\tStatus:',status.flag_strings())


if __name__ == '__main__':
  import sys
  sys.exit(status())

