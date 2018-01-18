#!/usr/bin/env python

import sys
import time

import scrollphat
import smbus
bus = smbus.SMBus(1)
for device in range(128):
    bus.read_byte(device)
    print "i2c ",device

scrollphat.set_brightness(7)

for x in range(1, 10):
    try:
        scrollphat.write_string(str(x))
        time.sleep(0.35)
    except KeyboardInterrupt:
        scrollphat.clear()
scrollphat.clear()
sys.exit(-1)
