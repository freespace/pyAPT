__version__ = "0.01"
__author__ = "Shuning Bian"

__all__ = ['Message', 'Controller', 'MTS50', 'add_PID', 'clear_PIDs', 'OutOfRangeError', 'PRM1']

from pyAPT import message, controller, mts50, prm1

Message = message.Message
Controller = controller.Controller
MTS50 = mts50.MTS50
PRM1 = prm1.PRM1
OutOfRangeError = controller.OutOfRangeError

import pylibftdi

def add_PID(pid):
  """
  Adds a USB PID to the list of PIDs to look for when searching for APT
  controllers
  """
  pylibftdi.USB_PID_LIST.append(pid)

def clear_PIDs():
  """
  Clears all USB PIDs
  """
  l = pylibftdi.USB_PID_LIST
  while len(l):
    l.pop()

# XXX By default pylibftdi looks for devices with PID of 0x6001 and 0x6014
# which slows device listing and identification down when we JUST want to
# identify motion controllers. So we do this little dance here.
#
# If you are using a single class of controllers, just replace 0xfaf0 with
# the controller's PID. If more than one class is being used, add each class's
# PID.
#
# Note that we cannot simply do pylibftdi.USB_PID_LIST = [...] because that
# just modifies pylibftdi.USB_PID_LIST, not the list used by driver.py in the
# pylibftdi package.

clear_PIDs()
add_PID(0xFAF0)
