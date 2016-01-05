#!/usr/bin/env python
"""
Usage: python get_info.py [<serial>]

Gets the controller information of all APT controllers, or the one specified
"""
from __future__ import absolute_import
from __future__ import print_function

import pyAPT

from runner import runner_serial

@runner_serial
def info(serial):
  with pyAPT.Controller(serial_number=serial) as con:
    info = con.info()
    print('\tController info:')
    labels=['S/N','Model','Type','Firmware Ver', 'Notes', 'H/W Ver',
            'Mod State', 'Channels']

    for idx,ainfo in enumerate(info):
      print('\t%12s: %s'%(labels[idx], bytes(ainfo)))

if __name__ == '__main__':
  import sys
  sys.exit(info())



