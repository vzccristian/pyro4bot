#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this classes are an adaption of adafruit gpio class
# support three diferent moderboards
# ____________developed by paco andres____________________
from node.libs.gpio.GPIO import HARDWARE
from  node.libs.gpio.gpiodef import *
if HARDWARE == "RASPBERRY_PI":
    import RPi.GPIO as rpi_gpio

class RPi_PWM(object):
    """PWM implementation for the Raspberry Pi using the RPi.GPIO PWM library."""

    def __init__(self, rpi_gpio,pyro4id,pin,frec):
        self.rpi_gpio = rpi_gpio
        self.pyro4id = pyro4id
        self.pin = pin
        self.frec = frec
        self.pwm = self.rpi_gpio.PWM(pin, frec)

    def start(self, dutycycle, frequency_hz=2000):
        """Enable PWM output on specified pin.  Set to intiial percent duty cycle
        value (0.0 to 100.0) and frequency (in Hz).
        """
        if dutycycle < 0.0 or dutycycle > 100.0:
            raise ValueError('Invalid duty cycle value, must be between 0.0 to 100.0 (inclusive).')
        self.rpi_gpio.setup(self.pin, self.rpi_gpio.OUT)
        self.pwm = self.rpi_gpio.PWM(self.pin, frequency_hz)
        self.pwm.start(dutycycle)

    def ChangeDutyCycle(self, dutycycle):
        """Set percent duty cycle of PWM output on specified pin.  Duty cycle must
        be a value 0.0 to 100.0 (inclusive).
        """
        if dutycycle < 0.0 or dutycycle > 100.0:
            raise ValueError('Invalid duty cycle value, must be between 0.0 to 100.0 (inclusive).')
        self.pwm.ChangeDutyCycle(dutycycle)

    def ChangeFrequency(self, frequency_hz):
        """Set frequency (in Hz) of PWM output on specified pin."""
        self.pwm.ChangeFrequency(frequency_hz)

    def stop(self):
        """Stop PWM output on specified pin."""
        self.pwm.stop()


if HARDWARE == "RASPBERRY_PI":
    PWMCLS = RPi_PWM
