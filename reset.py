#!/usr/bin/env python
"""
Usage: python reset.py [<serial>]

Resets all controller parameters to their default EEPROM value.
"""
from __future__ import absolute_import
from __future__ import print_function
import pyAPT

from runner import runner_serial

@runner_serial
def reset(serial):
    with pyAPT.Controller(serial_number=serial) as con:
      print('\tResetting controller parameters to EEPROM defaults')
      con.reset_parameters()

if __name__ == '__main__':
  import sys
  sys.exit(reset())

