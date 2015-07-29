#!/usr/local/bin/python3.4

'''
Co-routines for dealing with batches of inverter parameters.

Each of these co-routines (unless otherwise stated) take a dictionary
of name:value pairs and are intended to process the output of a single
batch of values polled from the inverter.

It is suggested that `OrderedDict` are used to preserve the original order
of the keys.

.. moduleauthor:: paul sorenson
'''


import sys
import pprint
import csv
from .dateawarejsonenc import DateAwareJSONEncoder


def coroutine(func):
    '''
    Decorator that initialises the co-routine.  Note that one
    downside of using this is that sphinx autodoc wont grok
    the parameter lists of the underlying co-routine.
    '''
    def _f(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g

    return _f


@coroutine
def tee(ltarget):
    '''
    Co-routine for splitting data to 1 or more targets.
    
    Note the developer needs to take responsbility to obey semantics of data
    passed in this way.  Eg if the data is a generator then it is unlikely the
    targets beyond the first one will see the same data.
    '''
    while True:
        d = (yield)
        for target in ltarget:
            target.send(d)


@coroutine
def tostream(fout=None, flush=False):
    if fout is None:
        fout = sys.stdout

    while True:
        fout.write((yield))
        if flush:
            fout.flush()


@coroutine
def prettyprint(fout=None):

    if fout is None:
        fout = sys.stdout
    
    pp = pprint.PrettyPrinter(stream=fout)

    while True:
        d = (yield)
        pp.pprint(d)


@coroutine
def tocsv(fout=None):

    if fout is None:
        fout = sys.stdout
        writehdr = True
    else:
        writehdr = False if fout.tell() else True

    d = (yield)
    wr = csv.DictWriter(fout, fieldnames=d.keys())
    if writehdr:
        wr.writeheader()
    wr.writerow(d)
    while True:
        d = (yield)
        wr.writerow(d)


@coroutine
def tojson(target, enc=None):
    '''
    Co-routine that JSON encodes input and sends to target.

    :param target: downstream co-routine.

    :param enc: use alternative JSON encoder.  If not specified
        a :class:`DateAwareJSONEncoder` is used.
    '''

    if enc is None:
        enc = DateAwareJSONEncoder()
    while True:
        target.send(enc.encode((yield)))


@coroutine
def bytes2str(target, enc='utf-8'):
    while True:
        target.send((yield).decode(enc))
