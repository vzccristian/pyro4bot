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
class alphainfrarredobs(control.Control):
    __REQUIRED = []

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RIGHT, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self.LEFT, GPIO.IN, GPIO.PUD_UP)
        self.init_workers(self.worker)

    def worker(self):
        while self.worker_run:
            self.DR_status = GPIO.input(self.RIGHT)
            self.DL_status = GPIO.input(self.LEFT)
            # print("left: {}, right: {}".format(self.DR_status, self.DL_status))
            time.sleep(self.frec)

    @Pyro4.expose
    def get_ir(self):
        return (self.DL_status, self.DR_status)
