#!/usr/bin/env python
"""
Usage: python get_status.py [<serial>]

Gets the status of all APT controllers, or of the one specified
"""
import pylibftdi
import pyAPT

def status(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    status = con.status()
    print '\tController status:'
    print '\t\tPosition: %.2fmm'%(status.position)
    print '\t\tVelocity: %.2fmm'%(status.velocity)
    print '\t\tStatus:',status.flag_strings()


def main(args):
  if len(args)>1:
    serial = args[1]
  else:
    serial = None

  if serial:
    status(serial)
    return 0
  else:
    print 'Looking for APT controllers'
    drv = pylibftdi.Driver()
    controllers = drv.list_devices()

    if controllers:
      for con in controllers:
        print 'Found %s %s S/N: %s'%con
        status(con[2])

      return 0
    else:
      print '\tNo APT controllers found. Maybe you need to specify a PID'
      return 1

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

