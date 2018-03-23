#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
import spidev


@Pyro4.expose
class spiservice (control.Control):
    __REQUIRED = ["gpioservice"]

    def __init__(self):
        self.spi = spidev.SpiDev()
        self.gpioservice.spi_setup(self.pyro4id)
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 7629



if __name__ == "__main__":
    pass
