#!/usr/bin/env python
"""
Usage: python get_status.py <acceleration (mm/s/s)> <max velocity (mm/s) [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
from __future__ import absolute_import
from __future__ import print_function
import pylibftdi
import pyAPT

def set_vel_params(serial, acc, max_vel):
  with pyAPT.MTS50(serial_number=serial) as con:
    print('\tSetting new velocity parameters',acc,max_vel)
    con.set_velocity_parameters(acc, max_vel)
    min_vel, acc, max_vel = con.velocity_parameters()
    print('\tNew velocity parameters:')
    print('\t\tMin. Velocity: %.2fmm'%(min_vel))
    print('\t\tAcceleration: %.2fmm'%(acc))
    print('\t\tMax. Velocity: %.2fmm'%(max_vel))

def main(args):
  if len(args)<3:
    print(__doc__)
    return 1

  acc = float(args[1])
  max_vel = float(args[2])

  if len(args)>3:
    serial = args[3]
  else:
    serial = None

  if serial:
    set_vel_params(serial, acc, max_vel)
    return 0
  else:
    print('Looking for APT controllers')
    drv = pylibftdi.Driver()
    controllers = drv.list_devices()

    if controllers:
      for con in controllers:
        print('Found %s %s S/N: %s'%con)
        set_vel_params(con[2], acc, max_vel)

      return 0
    else:
      print('\tNo APT controllers found. Maybe you need to specify a PID')
      return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

