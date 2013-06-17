#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
import pyAPT

from runner import runner_serial

@runner_serial
def get_vel_params(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    min_vel, acc, max_vel = con.velocity_parameters()
    print '\tController velocity parameters:'
    print '\t\tMin. Velocity: %.2fmm/s'%(min_vel)
    print '\t\tAcceleration: %.2fmm/s/s'%(acc)
    print '\t\tMax. Velocity: %.2fmm/s'%(max_vel)

if __name__ == '__main__':
  import sys
  sys.exit(get_vel_params())

