#!/usr/local/bin/python3.4

'''
Monitoring software for Aurora (now ABB) inverter via 'affable'
RS-485 to WiFi interface.

The kit came with a CD with windows software: Power 1 Aurora which
seems to work pretty well.  Since I don't want to run windows 24/7
to monitor the PV it is not a monitoring option.

From curtronics.com we have open source aurora software written in C.
It expects a serial device and can be made to work indirectly using socat:

``socat PTY,link=$HOME/dev/solar,raw TCP4:192.168.1.140:8899``

A sample aurora command looks like so:

``aurora -a2 -A -Y8 -w25 -M5 -d0 -D -j -U 50 -s -t -n  ~/dev/solar``

I found I had to use the -U option to specify a delay otherwise the reads
were unreliable.

I inspected the auroramon-1.8.8 code as well as running it in verbose mode
to inspect the data.

.. note::
    The Wifi adapter will happily allow you to connect even if the 
    inverter is powered off (ie the sun not shining).  So you need to 
    make a decision on how to deal with socket timeouts.

    The model I used initially which may not be optimal but works is to 
    use ``circusd`` to respawn the process and included a backoff timer
    when a socket timeout error occurs (the symptoms seen when the inverter
    is offline).

.. moduleauthor:: paul sorenson
'''


import sys
import socket as skt
import time
import datetime as dt
import functools as ft
from collections import OrderedDict
from argparse import ArgumentParser
import pyaurora as pv
import logging
from logging.config import dictConfig


dictConfig(pv.logconfig)
log = logging.getLogger('aurora')


operations = (
        #'getTime',
        #'getFirmwareRel', 
        'gridPowerAll', 
        'powerPeakToday',
        'dailyEnergy',
        'weeklyEnergy',
        #'last7Energy',
        'partialEnergy',
        'getEnergy10',
        'frequencyAll', 
        'gridVoltageAll', 
        'gridVoltageAverage', 
        'gridCurrentAll', 
        'bulkVoltageDcDc', 
        'in1Voltage',
        'in1Current',
        'in2Voltage',
        'in2Current',
        'pin1All', 
        'pin2All',
        'iLeakDcDc', 
        'iLeakInverter', 
        'boosterTemp',
    )
'''The inverter operations to be polled in each cycle.'''


def inverterpoll(inverterrdr, operations, target):
    '''
    Poll the inverter with a list of operations.

    :param inverterrdr: function that can issue commands and return
        response.  In general it accepts a command and subcommand (which
        may be None).
    :param operations: sequence of strings.  The current implementation 
        looks up the relevant command, subcommand, decoder and formatter
        to poll that value.
    :param target: coroutine that accepts a dict (actually an ordered dict).
    '''
    now = dt.datetime.now()
    log.debug('polling at {0}'.format(now))

    od = OrderedDict()
    utc = dt.datetime.utcnow()
    od['utc'] = utc

    for ssc in operations:
        cmd, sc, (decoder, fmt) = pv.command.allops[ssc]
        resp = inverterrdr(cmd, sc)
        od[ssc] = decoder(resp)

    target.send(od)


def main():

    a = ArgumentParser()
    a.add_argument('--host', default='192.168.1.140',
            help='WiFi adapter address (%(default)s).')
    a.add_argument('--port', type=int, default=8899,
            help='WiFi adapter port (%(default)s).')
    a.add_argument('--inv-addr', type=int, default=2,
            help='Inverter address (%(default)s)')
    a.add_argument('--read-delay', type=float, default=0.05,
            help='Time between command and read (%(default)f).')
    a.add_argument('--connect-timeout', type=float, default=None,
            help='Specify a timeout in seconds for connecting.')
    a.add_argument('--default-timeout', type=float, default=5.0,
            help='Set a default socket timeout in seconds (%(default)s).')
    a.add_argument('--loop-interval', type=int, default=10,
            help='''Time between inverter polls.  If set to zero, the inverter
is polled a single time and the process exits (%(default)s).
Note that changing this may affect the relevance of some commands eg
"energy in last 10 seconds".''')
    a.add_argument('--backoff', type=int, default=60, 
            help='''Sleep time after a socket timeout error (%(default)s).  The inverter
goes offline each night and requests result in socket timeout and subsequent process
exit.  This timeout is intended to reduce the frequency of spawning processes during
the night.''')
    a.add_argument('--csv', help='''Optionally write CSV to file.  The name
may contain `strftime` format strings.  If the string is "stdout" the CSV
output will be directed to `sys.stdout`.''')
    opt = a.parse_args()

    log.info('aurora starting')
    log.debug(opt)

    if opt.csv:
        if opt.csv == 'stdout':
            toutput = pv.tocsv(None)
        else:
            csvname = dt.datetime.now().strftime(opt.csv)
            toutput = pv.tocsv(open(csvname, 'a'))
    else:
        toutput = pv.prettyprint()


    with skt.create_connection((opt.host, opt.port), 
            opt.connect_timeout) as sock:

        if opt.default_timeout:
            sock.settimeout(opt.default_timeout)

        inverterrdr = ft.partial(pv.execcmd, sock, opt.inv_addr, 
                readdelay=opt.read_delay)

        try:
            if opt.loop_interval:
                pv.scheduler(opt.loop_interval, inverterpoll,
                    inverterrdr=inverterrdr, operations=operations,
                    target=toutput)
            else:
                inverterpoll(inverterrdr, operations, target=toutput)

        except skt.timeout:
            log.error('Socket timed out, application will exit')
            if opt.backoff:
                log.info('Backing off for {0} seconds.'.format(opt.backoff))
                time.sleep(opt.backoff)
        except KeyboardInterrupt:
            log.warning('Ctrl-C received, application will exit')

    log.info('aurora exiting')


if __name__ == '__main__':
    main()

