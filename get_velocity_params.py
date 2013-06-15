#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
import pylibftdi
import pyAPT

def get_vel_params(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    min_vel, acc, max_vel = con.velocity_parameters()
    print '\tController velocity parameters:'
    print '\t\tMin. Velocity: %.2fmm/s'%(min_vel)
    print '\t\tAcceleration: %.2fmm/s/s'%(acc)
    print '\t\tMax. Velocity: %.2fmm/s'%(max_vel)

def main(args):
  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    get_vel_params(serial)
    return 0
  else:
    print 'Looking for APT controllers'
    drv = pylibftdi.Driver()
    controllers = drv.list_devices()

    if controllers:
      for con in controllers:
        print 'Found %s %s S/N: %s'%con
        get_vel_params(con[2])

      return 0
    else:
      print '\tNo APT controllers found. Maybe you need to specify a PID'
      return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

