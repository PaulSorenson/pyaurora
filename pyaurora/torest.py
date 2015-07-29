#!/usr/local/bin/python3.4

'''
Simple rest co-routine.

.. moduleauthor:: paul sorenson
'''


from .output import coroutine
import requests as req


@coroutine
def torest(url, datavar):
    while True:
        data = {datavar: (yield)}
        resp = req.post(url, data=data)
        print(resp.text)
