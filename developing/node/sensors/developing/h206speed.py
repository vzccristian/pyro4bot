#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
from node.libs.gpio.GPIO import *


@Pyro4.expose
class h206speed(control.Control):
    __REQUIRED = ["MD", "MI", "gpioservice"]

    def __init__(self):
        self.cont_MD = 0
        self.cont_MI = 0
        self.GPIO=GPIOCLS(self.gpioservice,self.pyro4id)
        self.GPIO.setup([self.MD,self.MI],IN,PUD_DOWN)
        self.GPIO.add_event_detect(self.MD,RISING,self.pulseMD,20)
        self.GPIO.add_event_detect(self.MI,RISING,self.pulseMI,20)
        self.init_workers(self.worker)

    def pulseMD(self,channel):
        self.cont_MD = self.cont_MD + 1
        print("MD: {}".format(self.cont_MD))


    def pulseMI(self,channel):
        self.cont_MI = self.cont_MI + 1
        print("MI: {}".format(self.cont_MI))

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)


if __name__ == "__main__":
    pass
