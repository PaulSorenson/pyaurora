#!/usr/local/bin/python3.4

'''
Test post aurora data.

.. moduleauthor:: paul sorenson
'''


from .output import coroutine
import requests as req


@coroutine
def topost(url):
    '''
    Co-routine for posting inverter data to web service.

    The incoming data should be encoded as JSON.
    '''
    while True:
        data = (yield)
        resp = req.post(url, data=data)

