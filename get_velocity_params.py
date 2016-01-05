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
def get_vel_params(serial):
  with pyAPT.MTS50(serial_number=serial) as con:
    min_vel, acc, max_vel = con.velocity_parameters()
    raw_min_vel, raw_acc, raw_max_vel = con.velocity_parameters(raw=True)
    print('\tController velocity parameters:')
    print('\t\tMin. Velocity: %.2fmm/s (%d)'%(min_vel, raw_min_vel))
    print('\t\tAcceleration: %.2fmm/s/s (%d)'%(acc, raw_acc))
    print('\t\tMax. Velocity: %.2fmm/s (%d)'%(max_vel, raw_max_vel))

if __name__ == '__main__':
  import sys
  sys.exit(get_vel_params())

