#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


@Pyro4.expose
class l298n(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.gpioservice.setup(
            [self.IN1, self.IN2, self.IN3, self.IN4], GPIO.OUT, self.pyro4id)
        self.gpioservice.pwm_init(self.ENA, 100, self.pyro4id)
        self.gpioservice.pwm_init(self.ENB, 100, self.pyro4id)
        self.gpioservice.pwm_start((self.ENA, self.ENB), 100)
        self.stop()
        print self.gpioservice.status()
        self.init_workers(self.worker)

    def worker(self):
        try:
            while self.worker_run:
                time.sleep(self.frec)
        except:
            pass

    def forward(self, DCA=100):
        self.gpioservice.pwm_changedutycycle((self.ENA, self.ENB), DCA)
        self.gpioservice.output(self.IN1, 1)
        self.gpioservice.output(self.IN2, 0)
        self.gpioservice.output(self.IN3, 0)
        self.gpioservice.output(self.IN4, 1)

    def stop(self, DCA=0):
        self.gpioservice.pwm_changedutycycle((self.ENA, self.ENB), DCA)
        self.gpioservice.output(self.IN1, 0)
        self.gpioservice.output(self.IN2, 0)
        self.gpioservice.output(self.IN3, 0)
        self.gpioservice.output(self.IN4, 0)

    def backward(self, DCA=100):
        self.gpioservice.pwm_changedutycycle((self.ENA, self.ENB), DCA)
        self.gpioservice.output(self.IN1, 0)
        self.gpioservice.output(self.IN2, 1)
        self.gpioservice.output(self.IN3, 1)
        self.gpioservice.output(self.IN4, 0)

    def setvel(self, DCA, DCB):
        self.gpioservice.pwm_changedutycycle(self.ENA, DCA)
        self.gpioservice.pwm_changedutycycle(self.ENB, DCB)
        self.gpioservice.output(self.IN1, 1)
        self.gpioservice.output(self.IN2, 0)
        self.gpioservice.output(self.IN3, 1)
        self.gpioservice.output(self.IN4, 0)

    def left(self, DCA=100):
        self.setvel(0, DCA)

    def right(self, DCA=100):
        self.setvel(DCA, 0)


if __name__ == "__main__":
    pass
