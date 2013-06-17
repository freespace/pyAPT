#!/usr/bin/env python
"""
Usage: python identify.py [<serial>]

Finds all APT controllers and flashes their activity lights
"""
import time
import pyAPT

from runner import runner_serial

@runner_serial
def identify(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    print '\tIdentifying controller'
    con.identify()


if __name__ == '__main__':
  import sys
  sys.exit(identify())

