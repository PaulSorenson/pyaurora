# pyaurora
Python code for polling Aurora PV (photo voltaic) Inverter via WiFi.

This package contains code poll an Aurora (now ABB?) PV inverter.  It borrows concepts and 
constants from C code in aurora-1.8.8.  The key motivation for writing it was to read directly from a WiFi - RS-485
device and it reads only a subset of the data that aurora does.
