#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


@Pyro4.expose
class gpioinfrared(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(False)
        # GPIO.setup(self.setup[0],GPIO.IN,GPIO.PUD_UP)
        # GPIO.setup(self.setup[1],GPIO.IN,GPIO.PUD_UP)
        # this line is the last line in constructor method
        super(gpioinfrared, self).__init__(self.worker)

    def worker(self):
        while self.worker_run:
            # self.IR[0]=GPIO.input(self.setup[0])
            # self.IR[1]=GPIO.input(self.setup[1])
            # write here code for your sensor
            time.sleep(self.frec)
# here your methods

    def get_ir(self):
        return self.IR


if __name__ == "__main__":
    pass