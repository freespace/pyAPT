#!/usr/bin/env python

"""
Simple class to make construction and decoding of message bytes easier.

Based on APT Communication Protocol Rev. 7 (Thorlabs)

"""
import struct as st
from collections import namedtuple

_Message = namedtuple(
  '_Message',
  ['messageID', 'param1', 'param2', 'dest', 'src', 'data'])

class Message(_Message):
  @classmethod
  def unpack(cls, databytes):
    Header = namedtuple('Header', ['messageID', 'param1', 'param2', 'dest','src'])
    hd = Header._make(st.unpack('<HBBBB',databytes[:6]))

    # if MSB of dest is set, then there is additional data to follow
    if hd.dest & 0x80:
      datalen = hd.param1 | (hd.param2<<8)
      data=st.unpack('<%dB'%(datalen), databytes[6:])

      return Message( hd.messageID,
                      dest = hd.dest,
                      src = hd.src,
                      data = data)
    else:
      return Message( hd.messageID,
                      param1 = hd.param1,
                      param2 = hd.param2,
                      dest = hd.dest,
                      src = hd.src)

  def __new__(self, messageID, dest=0x50, src=0x01, param1=0, param2=0, data=None):
    assert(type(messageID) == int)
    if data:
      assert(param1 == 0 and param2 == 0)
      assert(type(data) in [list, tuple])
      return super(Message, self).__new__(Message,
                                          messageID,
                                          None,
                                          None,
                                          dest,
                                          src,
                                          data)
    else:
      assert(type(param1) == int)
      assert(type(param2) == int)
      return super(Message, self).__new__(Message,
                                          messageID,
                                          param1,
                                          param2,
                                          dest,
                                          src,
                                          None)

  def pack(self, verbose=False):
    """
    Returns a byte array representing this message packed in little endian
    """
    if self.data:
      """
      <: little endian
      H: 2 bytes for message ID
      H: 2 bytes for data length
      B: unsigned char for dest
      B: unsigned char for src
      %dB: %d bytes of data
      """
      datalen = len(self.data)
      ret = st.pack(  '<HHBB%dB'%(datalen),
                      self.messageID,
                      datalen,
                      self.dest|0x80,
                      self.src,
                      *self.data)
    else:
      """
      <: little endian
      H: 2 bytes for message ID
      B: unsigned char for param1
      B: unsigned char for param2
      B: unsigned char for dest
      B: unsigned char for src
      """
      ret = st.pack(  '<HBBBB',
                      self.messageID,
                      self.param1,
                      self.param2,
                      self.dest,
                      self.src)
    if verbose:
      print bytes(self),'=',map(lambda x:hex(ord(x)), ret)

    return ret

  def __eq__(self, other):
    """
    We don't compare the underlying namedtuple because we consider data of
    [1,2,3,4,5] and (1,2,3,4,5) to be the same, while python doesn't.
    """
    return self.pack() == other.pack()

def pack_unpack_test():
  """
  If we pack a message, then unpack it, we should recover the message exactly.
  """
  a = Message(0x0223,data=[1,2,3,4,5])
  s = a.pack(True)
  b = Message.unpack(s)
  assert a == b
