

'''
:mod:`cozmq` - coroutines for zeromq
====================================

Note that we are using send_string(), recv_string().  Since the data is
a JSON string this should be fine but a more general solution would send/recv
bytes and encode/decode as necessary.

:mod:`zmq` has send_json() and recv_json() however it doesn't look like there is
an easy way to specify and alternate encoder (eg to handle dates).

.. moduleauthor:: paul sorenson
'''


from .output import coroutine
import logging
try:
    import zmq
except:
    log.warning('cannot import zmq')


@coroutine
def tozmq(sock):
    while True:
        sock.send_string((yield))


# not a coroutine - pulls from a zmq socket
def fromzmq(sock, target):
    while True:
        target.send(sock.recv_string())


