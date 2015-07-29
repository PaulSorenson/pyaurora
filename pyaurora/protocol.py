#!/usr/local/bin/python3.4

'''
Monitoring software for Aurora (now ABB) inverter via 'affable'
RS-485 to WiFi interface.

The kit came with a CD with windows software: Power 1 Aurora which
seems to work pretty well.  Since I don't want to run windows 24/7
to monitor the PV it is not a long term option.

From curtronics.com we have open source aurora software written in C.
It expects a serial device and can be made to work indirectly using socat:

``socat PTY,link=$HOME/dev/solar,raw TCP4:192.168.1.140:8899``

A sample aurora command looks like so:

``aurora -a2 -A -Y8 -w25 -M5 -d0 -D -j -U 50 -s -t -n  ~/dev/solar``

I found I had to use the -U option to specify a delay otherwise the reads
were unreliable.

I started with the aurora in verbose mode and inspecting the code.

.. moduleauthor:: paul sorenson
'''


import time
import datetime as dt
import codecs
import socket as skt
import struct
from argparse import ArgumentParser
import logging


log = logging.getLogger('aurora')


MAXRESP = 16
'It is probably more like 10 but not sure.'''


class CRCException(Exception):

    def __init__(self, buf, crc):
        self.buf = buf
        self.crc = crc

    def __str__(self):
        return 'buf: {0} calculated CRC: {1}'.format(
                bytes2hex(self.buf),
                bytes2hex(self.crc))


def tolong(buf):
    '''
    Convert 4 bytes to long.
    '''
    return struct.unpack('!l', buf[:4])[0]


def getlong(buf):
    return tolong(buf[2:])


def tofloat(buf):
    '''
    Convert 4 byte value to float.

    :param buf: the first four bytes of this bytes buf are converted
        to a float.
    '''
    return struct.unpack('!f', buf[:4])[0]


def getfloat(buf):
    '''
    Take an inverter response and extract float value from it.
    This does not apply to every command but does apply to most
    if not all of the getDsp sub commands.
    '''
    return tofloat(buf[2:])


def getstring(buf):
    return str(buf[2:])


def gettime(buf):
    l = struct.unpack('!L', buf[2:])[0]
    return dt.date.fromtimestamp(l)


def bytes2hex(buf):
    '''
    return hex string encoding of bytes.
    '''
    return codecs.encode(buf, 'hex_codec')


def word2bytearray(i):
    b = bytearray()
    b.append(i & 0xff)
    b.append(i // 256)
    return b


def crc16(buf):
    '''
    Create Aurora protocol compatible CRC16 from sequence of bytes.
    '''
    POLY = 0x8408
    MASK = 0xffff
    BIT = 0x0001

    crc = 0xffff

    if len(buf) == 0:
        return ~crc & MASK

    for data in buf:
        for i in range(8):
            if ((crc & BIT) ^ (data & BIT)):
                crc = ((crc >> 1) ^ POLY) & MASK
            else:
                crc >>= 1
            data >>= 1

    return ~crc & MASK


def addcrc(buf):
    '''
    Calculate CRC and append to buffer bytes.
    '''
    return buf + word2bytearray(crc16(buf))


def stripcrc(buf):
    '''
    Strip CRC from bytes.  Throws Exception if CRC doesn't 
    match.
    '''
    data = buf[:-2]
    tcrc = buf[-2:]
    crc = word2bytearray(crc16(data))
    #print(buf, data, tcrc, crc)
    if crc == buf[-2:]:
        return data
    else:
        raise CRCException(buf, crc)


def pad(buf, sz):
    '''
    Pad buffer with nulls to sz.
    '''
    PAD = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    if sz > len(PAD):
        raise Exception('sz must be <= {0}'.format(len(PAD)))

    return buf + PAD[:(sz - len(buf))]


def makecmd(addr, cmd, subcmd=None):
    '''
    Construct a command buffer from inverter address and cmd.

    :param addr: inverter address 1..31 or 1..63 depending on model.

    :param cmd: aurora command byte.
    '''

    log.debug('cmd: {0} subcmd: {1}'.format(cmd, subcmd))

    buf = bytearray([b for b in (addr, cmd, subcmd, 0) if b is not None])

    return addcrc(pad(buf, 8))


def execcmd(sock, addr, cmd, subcmd=None, readdelay=0.05):
    '''
    Send a command and return a response.

    :param sock: open socket for communication.

    :param addr: inverter address (eg 2).
    
    :param cmd: inverter command.

    :param readdelay: wait this long (seconds) before reading
        from the socket.

    :returns: byte array of response less CRC.

    :raises: CRCException if the calculated CRC does not match the 
        response buffer.
    '''
    cmdbuf = makecmd(addr, cmd, subcmd)
    log.debug('cmd buffer: {0}'.format(bytes2hex(cmdbuf)))
    sock.send(cmdbuf)
    time.sleep(readdelay)
    respbuf = sock.recv(MAXRESP)
    log.debug('response buffer: {0}'.format(bytes2hex(respbuf)))

    return stripcrc(respbuf)

