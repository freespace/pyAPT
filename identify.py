#!/usr/bin/env python
"""
Usage: python identify.py [<serial>]

Finds all APT controllers and flashes their activity lights
"""
from __future__ import absolute_import
from __future__ import print_function
import time
import pyAPT
import sys
from runner import runner_serial

@runner_serial
def identify(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    print('\tIdentifying controller')
    con.identify()
    print('\n>>>>Press enter to continue')
    sys.stdin.readline()

if __name__ == '__main__':
  sys.exit(identify())

