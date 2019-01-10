#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
from node.libs.gpio.SPI import *


@Pyro4.expose
class spiservice (control.Control):
    __REQUIRED = ["gpioservice"]

    def __init__(self):
        self.devices={0:None, 1:None}
        #self.SPI =SPICLS()
        self.gpioservice.spi_setup(self.pyro4id)
        #print(self.status)

    @property
    def status(self):
        return self.devices

    def register(self, device, proxy):
        """register a proxy in  one device"""
        if device in self.devices:
            if self.devices[device] is None:
                self.devices[device]=proxy
                return True
            else:
                print(("Device {} in use".format(device)))
                return False
        else:
            return False



if __name__ == "__main__":
    pass
