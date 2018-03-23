#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
from node.libs.pyro4bot_gpio import *


class IR_remote_control(control.Control):
    __REQUIRED = ["gpioservice","IR_receiver"]

    def __init__(self):
        self.GPIO=bot_GPIO(self.gpioservice,self.pyro4id)
        self.GPIO.setup(self.IR_receiver,IN)
        self.init_workers(self.worker)
        #print(self.GPIO.STATUS)

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)
            #print(self.line)
