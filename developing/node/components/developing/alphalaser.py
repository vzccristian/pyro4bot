#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


class alphaultrasound(control.Control):
    __REQUIRED = []

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.TRIG, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ECHO, GPIO.IN)
        self.middleDistance = 0
        self.init_workers(self.worker,)

    def worker(self):
        while self.worker_run:
            self.middleDistance = self.Distance()
            print("MiddleDistance = %0.2f cm" % middleDistance)
            time.sleep(self.frec)
    #         if middleDistance <= 20:
    #             Ab.stop()
    # #			time.sleep(0.5)
    #             ServoAngle(5)
    #             time.sleep(1)
    #             rightDistance = Distance()
    #             print("RightDistance = %0.2f cm" % rightDistance)
    # #			time.sleep(0.5)
    #             ServoAngle(180)
    #             time.sleep(1)
    #             leftDistance = Distance()
    #             print("LeftDistance = %0.2f cm" % leftDistance)
    # #			time.sleep(0.5)
    #             ServoAngle(90)
    #             time.sleep(1)
    #             if rightDistance < 20 and leftDistance < 20:
    #                 Ab.backward()
    #                 time.sleep(0.3)
    #                 Ab.stop()
    #             elif rightDistance >= leftDistance:
    #                 Ab.right()
    #                 time.sleep(0.3)
    #                 Ab.stop()
    #             else:
    #                 Ab.left()
    #                 time.sleep(0.3)
    #                 Ab.stop()
    #             time.sleep(0.3)
    #         else:
    #             Ab.forward()
    #             time.sleep(0.02)

    def Distance(self):
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
