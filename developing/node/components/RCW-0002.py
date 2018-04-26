#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


class RCW - 0002 (control.Control):
    __REQUIRED = ["gpioservice", "IN", "OUT", "pyro4id"]

    def __init__(self):
        self.gpioservice.setup([self.IN], GPIO.IN, self.pyro4id)
            self.gpioservice.setup(
                [self.OUT], GPIO.OUT, self.pyro4id)

    def worker(self):
        pass
