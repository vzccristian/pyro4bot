#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object

import time
from node.libs import control, gpiodef, utils
import Pyro4
import RPi.GPIO as GPIO


def get_function(pin):
    """ return gpio_function trapping errors"""
    try:
        return GPIO.gpio_function(pin)
    except:
        return -2


@Pyro4.expose
class gpioservice(control.Control):
    __REQUIRED = ["gpio_mode"]

    def __init__(self):
        if not hasattr(self, 'frec'):
            self.frec = 0.02
        self.gpio_mode = gpiodef.modes.get(self.gpio_mode, GPIO.BCM)
        GPIO.setmode(self.gpio_mode)
        GPIO.setwarnings(False)
        self.create_gpio()

    def create_gpio(self):
        """ create a new dict for gpi in mode bcm or board. use gpiodef.gpioport definition
            set empty pwm and event_detect this funcionality no is implemented yet"""
        self.pwm = {}
        self.event_detect = {}
        if self.gpio_mode == GPIO.BCM:
            self.gpio = {x[1]: [k, x[0], get_function(x[1]), None]
                         for k, x in gpiodef.gpioport.items() if x[1] != None}
        else:
            self.gpio = {k: [k, x[0], get_function(k), None]
                         for k, x in gpiodef.gpioport.items() if x[2] != None}

    def status(self, pins=None, _str=False):
        if pins is None:
            pins = self.gpio.keys()
        if type(pins) not in (list, tuple):
            pins = (pins,)
        if _str:
            return {k: [x[0], x[1], gpiodef.status[x[2]], x[3]] for (k, x) in self.gpio.items() if k in pins}
        else:
            return {k: x for (k, x) in self.gpio.items() if k in pins}

    def setup(self, pins, value, proxy):
        """ set a pin list in service gpio with initial value.
        there are a relationship between proxy id and  pin number
        """
        if type(pins) not in (list, tuple):
            pins = (pins,)
        notavailable = [
            x for x in pins if x in self.gpio and self.gpio[x][3] is not None]
        if len(notavailable) != 0:
            print ("GPIO pins in use:", notavailable)
            return False
        for k in pins:
            if k in self.gpio:
                self.gpio[k][2] = value
                self.gpio[k][3] = proxy
                if value in (GPIO.IN, GPIO.OUT):
                    GPIO.setup(k, value)
        return True

    def i2c_setup(self, proxy):
        if self.gpio_mode == GPIO.BCM:
            return self.setup((2, 3), GPIO.I2C, proxy)
        else:
            return self.setup((3, 5), GPIO.I2C, proxy)

    def spi_setup(self, proxy):
        if self.gpio_mode == GPIO.BCM:
            return self.setup((7, 8, 9, 10, 11), GPIO.SPI, proxy)
        else:
            return self.setup((19, 21, 23, 24, 26), GPIO.SPI, proxy)

    def get_mode(self, _str=False):
        """ Return mode bcm 11 or BOARD 10 active if _str return mode for human readable"""
        if _str:
            return modes[GPIO.getmode()]
        else:
            return GPIO.getmode()

    def input(self, pin):
        """ read a pin value """
        if pin in self.gpio:
            return GPIO.input(pin)
        else:
            return None

    def output(self, pin, value):
        """ send valid value (True or False ) to gpio pin"""
        try:
            if pin in self.gpio and self.gpio[pin][2] == GPIO.OUT:
                GPIO.output(pin, value)
        except:
            print("Error gpioservice output")

    def PWM(self, pin, frec, proxy):
        """ create a new pwm object if max_pwm is no exceded"""
        if len(self.pwm) > gpiodef.max_pwm:
            print "GPIO: Error Max PWM exceded"
            return False
        if pin in self.gpio and self.gpio[pin][3] == proxy:
            GPIO.setup(pin,GPIO.OUT)
            self.pwm[pin]=GPIO.PWM(pin,frec)
            self.gpio[pin][2] = 10
            self.gpio[pin][3] = proxy
            return True
        else:
            print "GPIO: Error no pin for PWM or not setup"
            return False

    def start(self, pins, dc=50):
        """ init a pwm objects with ids=pins. dc is pulse width between 0 and 100"""
        dc = 100 if dc > 100 else dc
        dc = 0 if dc < 0 else dc
        if type(pins) not in (list, tuple):
            pins = (pins,)
        for pin in pins:
            if pin in self.pwm:
                self.pwm[pin].start(dc)

    def stop(self, pins):
        """ stop same pwms objects"""
        if type(pins) not in (list, tuple):
            pins = (pins,)
        for pin in pins:
            if pin in self.pwm:
                self.pwm[pin].stop()

    def ChangeFrequency(self, pins, freq):
        """to change the frequency where freq is the new frequency in Hz"""
        if type(pins) not in (list, tuple):
            pins = (pins,)
        for pin in pins:
            if pin in self.pwm:
                self.pwm[pin].ChangeFrequency(freq)

    def ChangeDutyCycle(self, pins, dc=50):
        """ to change pulse width dc is a value between 0 and 100"""
        dc = 100 if dc > 100 else dc
        dc = 0 if dc < 0 else dc
        if type(pins) not in (list, tuple):
            pins = (pins,)
        for pin in pins:
            if pin in self.pwm:
                self.pwm[pin].ChangeDutyCycle(dc)

    def remove_pwm(self, pin):
        """ del a pwm object """
        if pin in self.pwm:
            del(self.pwm[pin])
            self.gpio[pin][2] = get_function(pin)

    def add_event_detect(self,pin,pyro4id,when,callback="hello",bouncetime=200):
        if pin in self.gpio and self.gpio[pin][3] == pyro4id:
            connector=utils.get_proxy(self.gpio[pin][3],self.botname)
            #GPIO.add_event_detect(pin,when,callback=None,bouncetime) #revisar conexion

    def remove_event_detect(self,pin,pyro4id):
        if pin in self.gpio and self.gpio[pin][3] == pyro4id:
            GPIO.remove_event_detect(pin) #revisar conexion

    def __del__(self):
        print "borrando"
        GPIO.cleanup()


if __name__ == "__main__":
    pass
    # import sys
    # import os
    # sys.path.insert(0, os.path.abspath(
    #     os.path.join(os.path.dirname(__file__), "../..")))
    # di = {"cls": "gpioservice", "mode": "BCM",
    #       "frec": 0.02, "enable": True, "worker_run": False}
    # pru = gpioservice([], **di)
