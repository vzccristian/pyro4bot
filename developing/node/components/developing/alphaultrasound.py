#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


class alphaultrasound(control.Control):
    """RCW-0002"""
    __REQUIRED = []

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.TRIG, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ECHO, GPIO.IN)
        self.middleDistance = 0
        self.start_worker(self.worker,)

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)
            self.middleDistance = self.distance()
            # print("MiddleDistance = %0.2f cm" % self.middleDistance)

    def distance(self):
        GPIO.output(self.TRIG, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.TRIG, GPIO.LOW)
        while not GPIO.input(self.ECHO):
            pass
        t1 = time.time()
        while GPIO.input(self.ECHO):
            pass
        t2 = time.time()
        return (t2 - t1) * 34000 / 2

    @Pyro4.expose
    def getDistance(self):
        # print("%0.2f cm" % self.middleDistance)
        return self.middleDistance
