#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All data defined in json configuration are attributes in your code object

import time
from node.libs import control, utils
from node.libs.gpio.GPIO import HARDWARE, GPIOCLS
import Pyro4




@Pyro4.expose
class gpioservice(control.Control):
    __REQUIRED = ["gpio_mode"]

    def __init__(self):
        self.HARDWARE = HARDWARE
        self.gpio_mode = modes.get(self.gpio_mode, BCM)
        self.HGPIO = GPIOCLS(mode=self.gpio_mode)
        self.create_gpio()


    def create_gpio(self):
        """ create a new dict for gpi in mode bcm or board. use gpiodef.gpioport definition
            set empty pwm and event_detect this funcionality no is implemented yet"""
        if self.gpio_mode == BCM:
            self.MAP = {x[1]: [k, x[0], self.HGPIO.get_function(x[1]), None]
                         for k, x in list(gpioport.items()) if x[1] != None}
        else:
            self.MAP = {k: [k, x[0], self.HGPIO.get_function(k), None]
                         for k, x in list(gpioport.items()) if x[2] != None}

    def status(self, pins=None, _str=False):
        if pins is None:
            pins = list(self.MAP.keys())
        if type(pins) not in (list, tuple):
            pins = (pins,)
        if _str:
            return {k: [x[0], x[1], status[x[2]], x[3]] for (k, x) in list(self.MAP.items()) if k in pins}
        else:
            return {k: x for (k, x) in list(self.MAP.items()) if k in pins}

    def setup(self, proxy, pins, mode, pull_up_down=PUD_OFF):
        """ set a pin list in service gpio with initial value.
        there are a relationship between proxy id and  pin number
        """
        if type(pins) not in (list, tuple):
            pins = (pins,)
        notavailable = [
            x for x in pins if x in self.MAP and self.MAP[x][3] is not None]
        if len(notavailable) != 0:
            print(("GPIO pins in use:", notavailable))
            return False
        for k in pins:
            if k in self.MAP:
                self.MAP[k][2] = mode
                self.MAP[k][3] = proxy
        return True

    def i2c_setup(self, proxy):
        if self.gpio_mode == BCM:
            return self.setup(proxy,(2, 3), 42)
        else:
            return self.setup(proxy,(3, 5), 42)

    def spi_setup(self, proxy):
        if self.gpio_mode == BCM:
            return self.setup(proxy,(7, 8, 9, 10, 11), 41)
        else:
            return self.setup(proxy,(19, 21, 23, 24, 26), 41)

    def get_mode(self, _str=False):
        """ Return mode bcm 11 or BOARD 10 active if _str return mode for human readable"""
        if _str:
            return modes[self.HGPIO.getmode()]
        else:
            return self.HGPIO.getmode()

    def PWM(self, pin, frec, proxy):
        """ create a new pwm object if max_pwm is no exceded"""
        if pin in self.MAP and self.MAP[pin][3] == proxy:
            self.MAP[pin][2] = 10
            self.MAP[pin][3] = proxy
            return True
        else:
            print("GPIO: Error no pin for PWM or not setup")
            return False


    def __del__(self):
        GPIO.cleanup()



if __name__ == "__main__":
    pass
