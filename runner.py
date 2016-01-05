from __future__ import absolute_import
from __future__ import print_function
#!/usr/bin/env python
import pylibftdi

def runner_serial(func):
  """
  Decorator for functions that take a serial number as the first argument,
  possibly with other arguments to follow
  """
  def inner():
    import sys
    args = sys.argv

    if len(args)>1:
      serial = args[1]
    else:
      serial = None

    if serial:
      func(serial)
      return 0
    else:
      print('Looking for APT controllers')
      drv = pylibftdi.Driver()
      controllers = drv.list_devices()

      if controllers:
        for con in controllers:
          print('Found %s %s S/N: %s'%con)
          func(con[2])
          print('')

        return 0
      else:
        print('\tNo APT controllers found. Maybe you need to specify a PID')
        return 1
  return inner

