#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in your code object

import time
from node.libs import control
import Pyro4
from node.libs.gpio.I2C import *


@Pyro4.expose
class i2cservice(control.Control):
    __REQUIRED = ["gpioservice"]

    def __init__(self):
        self.I2C = I2CCLS(0)
        self.gpioservice.i2c_setup(self.pyro4id)
        self.addr = self.I2C.detect_ports()

    @property
    def status(self):
        return self.addr

    def register(self, address, proxy):
        """register a proxy in a one address device"""
        if address in self.addr:
            self.addr[address].append(proxy)
            return True
        else:
            return False


if __name__ == "__main__":
    pass
