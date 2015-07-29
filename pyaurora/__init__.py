'''
pyaurora package

communicate with Aurora PV inverters via WiFi.

This code lends heavily from the C lanaguage aurora code from curtronics.com
I set out to write something specific to my setup which is a PVI-6000 inverter
with a WiFi to RS-485 converter.  The curtronics code can be made to work
with this WiFi converter using the linux `socat` command.

.. moduleauthor:: paul sorenson
'''

__version__ = '0.1'

from .logconfig import *
from .protocol import *
from .command import *
from .scheduler import scheduler
from .output import *

