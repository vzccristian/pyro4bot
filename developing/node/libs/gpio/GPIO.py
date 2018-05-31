#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this classes are an adaption of adafruit gpio class
# support three diferent moderboards
# ____________developed by paco andres____________________

from Platform import HARDWARE
import Pyro4
from node.libs.gpio.gpiodef import *
from node.libs.gpio.PWM import *
if HARDWARE == "RASPBERRY_PI":
    import RPi.GPIO as rpi_gpio


class RPiGPIO(object):
    """GPIO implementation for the Raspberry Pi using the RPi.GPIO library."""

    def __init__(self, service=None, pyro4id=None, mode=None):
        self.rpi_gpio = rpi_gpio
        self.SGPIO = service
        self.pyro4id = pyro4id
        self.setwarnings(False)
        # Setup board pin mode.
        if self.SGPIO is not None:
            mode = self.SGPIO.get_mode()
        self.setmode(mode)

    def setmode(self, mode):
        if mode == BOARD or mode == BCM:
            self.rpi_gpio.setmode(mode)
        elif mode is not None:
            raise ValueError(
                'Unexpected value for mode.  Must be BOARD or BCM.')
        else:
            # Default to BCM numbering if not told otherwise.
            self.rpi_gpio.setmode(BCM)

    def getmode(self):
        return self.rpi_gpio.getmode()

    def setwarnings(self, act=False):
        self.rpi_gpio.setwarnings(act)

    def status(self):
        if self.SGPIO is not None:
            return self.SGPIO.status()
        else:
            print("GPIO status not available")

    def get_function(self, pin):
        """ return gpio_function trapping errors"""
        try:
            return self.rpi_gpio.gpio_function(pin)
        except:
            return -2

    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUTPUT or INPUT.
        """
        if self.SGPIO is not None:
            self.SGPIO.setup(self.pyro4id, pin, mode, pull_up_down)
        self.rpi_gpio.setup(pin, mode, pull_up_down)

    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high).
        """
        self.rpi_gpio.output(pin, value)

    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.rpi_gpio.input(pin)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        # maybe rpi has a mass read...  it would be more efficient to use it if it exists
        return [self.rpi_gpio.input(pin) for pin in pins]

    def PWM(self, pin, frec):
        if self.SGPIO is not None:
            doit = self.SGPIO.PWM(pin, frec, self.pyro4id)
        else:
            doit = True
        if doit:
            return PWMCLS(self.rpi_gpio, self.pyro4id, pin, frec)
        else:
            return None

    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback'] = callback
        if bouncetime > 0:
            kwargs['bouncetime'] = bouncetime
        self.rpi_gpio.add_event_detect(pin, edge, **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.rpi_gpio.remove_event_detect(pin)

    def add_event_callback(self, pin, callback):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.
        """
        self.rpi_gpio.add_event_callback(pin, callback)

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to
        enable edge detection using add_event_detect() first.   Pin should be
        type IN.
        """
        return self.rpi_gpio.event_detected(pin)

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING,
        FALLING or BOTH.
        """
        self.rpi_gpio.wait_for_edge(pin, edge)

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none
        is specified.
        """
        if pin is None:
            self.rpi_gpio.cleanup()
        else:
            self.rpi_gpio.cleanup(pin)


if HARDWARE == "RASPBERRY_PI":
    GPIOCLS = RPiGPIO
