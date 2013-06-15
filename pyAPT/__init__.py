__version__ = "0.01"
__author__ = "Shuning Bian"

__all__ = ['Message', 'Controller', 'MTS50']

from pyAPT import message, controller, MTS50

Message = message.Message
Controller = controller.Controller
MTS50 = MTS50.MTS50

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

import pylibftdi
l = pylibftdi.USB_PID_LIST
while len(l):
  l.pop()
l.append(0xfaf0)
