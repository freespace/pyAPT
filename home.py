#!/usr/bin/env python
"""
Usage: python home.py [<serial>]

This program homes all APT controllers found, or of the one specified
"""

import time
import pyAPT

from runner import runner_serial

@runner_serial
def home(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    print '\tIdentifying controller'
    con.identify()
    print '\tHoming parameters:', con.request_home_params()
    print '\tHoming stage...',
    con.home(velocity=2)
    print 'homed'

if __name__ == '__main__':
  import sys
  sys.exit(home())

