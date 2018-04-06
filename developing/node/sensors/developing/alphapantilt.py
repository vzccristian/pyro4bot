#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
from node.libs.gpio.GPIO import *


@Pyro4.expose
class alphapantilt(control.Control):
    __REQUIRED = ["PAN", "TILT", "gpioservice"]

    def __init__(self):
        self.GPIO = GPIOCLS(self.gpioservice, self.pyro4id)
        self.GPIO.setup([self.PAN, self.TILT], OUT)
        self.cpan = self.GPIO.PWM(self.PAN, 60)
        self.ctilt = self.GPIO.PWM(self.TILT, 60)
        self.set_angle(self.PAN, self.cpan, 180)
        self.set_angle(self.TILT, self.ctilt, 180)

        print("HECHO")

    @control.flask("actuator")
    def set_angle(self, pin, pwm, angle):
        duty_cycle = (float(angle) / 24.0) + 2.5
        # activate the servo pin
        self.GPIO.output(pin, HIGH)
        # change the duty cycle to calculated value
        pwm.start(duty_cycle, 60)
        # send signal 0.5 seconds
        time.sleep(0.5)
        # deactivate the servo pin
        GPIO.output(pin, LOW)
        # change the duty cycle to 0
        pwm.stop()
