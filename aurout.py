#!/usr/local/bin/python3.4

'''
Aurora zmq receiver subscribes to ZMQ URL and processes JSON.

.. moduleauthor:: paul sorenson
'''


import sys
from argparse import ArgumentParser
import zmq
import pyaurora as pv
from pyaurora.cozmq import fromzmq
from pyaurora.torest import torest


def main():

    a = ArgumentParser()
    a.add_argument('--sub-url', default='tcp://127.0.0.1:8080',
            help='''Specify a zeromq URL to receive JSON to (%(default)s).''')
    opt = a.parse_args()

    #sink = pv.tostream(flush=True)
    sink = torest('http://obiwan.home.metrak.com:8888/aurora', 'inverter_data')

    context = zmq.Context()
    zock = context.socket(zmq.SUB)
    zock.connect(opt.sub_url)
    zock.setsockopt_string(zmq.SUBSCRIBE, '')

    fromzmq(zock, sink)

    log.info('aurout exiting')


if __name__ == '__main__':
    main()

