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

        self.init_workers()

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)
# here your methods


if __name__ == "__main__":
    pass
