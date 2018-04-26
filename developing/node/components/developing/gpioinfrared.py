#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


@Pyro4.expose
class gpioinfrared(control.Control):
    __REQUIRED = ["setup", "IR", "frec"]

    def __init__(self):
        self.init_workers(self.worker)

    def worker(self):
        while self.worker_run:
            # self.IR[0]=GPIO.input(self.setup[0])
            # self.IR[1]=GPIO.input(self.setup[1])
            # write here code for your component
            time.sleep(self.frec)

    @control.flask("sensor", 2)
    def get_ir(self):
        return self.IR


if __name__ == "__main__":
    pass
