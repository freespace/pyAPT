__version__ = "0.01"
__author__ = "Shuning Bian"

__all__ = ['Message', 'Controller', 'MTS50']

from pyAPT import message, controller, MTS50

Message = message.Message
Controller = controller.Controller
MTS50 = MTS50.MTS50

import pylibftdi
pylibftdi.USB_PID_LIST.insert(0,0xfaf0)
