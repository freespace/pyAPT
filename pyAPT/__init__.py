from __future__ import absolute_import
import pylibftdi

from pyAPT import message, controller, mts50, prm1

__version__ = "0.01"
__author__ = "Shuning Bian"

__all__ = ['Message', 'Controller', 'MTS50', 'OutOfRangeError', 'PRM1',
           'add_PID']

Message = message.Message
Controller = controller.Controller
MTS50 = mts50.MTS50
PRM1 = prm1.PRM1
OutOfRangeError = controller.OutOfRangeError

_PRODUCT_IDS = pylibftdi.USB_PID_LIST
_PRODUCT_IDS[:] = [0xFAF0]


def add_PID(pid):
    """
    Adds a USB PID to the list of PIDs to look for when searching for APT
    controllers
    """
    _PRODUCT_IDS.append(pid)
