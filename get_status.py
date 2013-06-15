#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
import pylibftdi
import pyAPT

def main(args):
  print 'Looking for APT controllers'
  drv = pylibftdi.Driver()
  controllers = drv.list_devices()

  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    controllers = filter(lambda x:x[2] == serial, controllers)

  if controllers:
    for con in controllers:
      print 'Found %s %s S/N: %s'%con
      with pyAPT.Controller(serial_number=con[2]) as con:
        pos,vel,status = con.get_status()
        print '\tController status:'
        print '\t\tPosition: %.2fmm'%(pos)
        print '\t\tVelocity: %.2fmm'%(vel)
        print '\t\tStatus:',status

      return 0
  else:
    print '\tNo APT controllers found. Maybe you need to specify a PID'
    return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

