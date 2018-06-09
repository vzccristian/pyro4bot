#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
from node.libs.gpio.GPIO import *


class tlc1543ad(control.Control):
    __REQUIRED = ["CS", "Clock", "Address", "DataOut", "line"]

    def __init__(self):
        self.GPIO=GPIOCLS(self.gpioservice,self.pyro4id)
        self.GPIO.setup((self.Clock,self.Address,self.CS),OUT)
        self.GPIO.setup(self.DataOut,IN,PUD_UP)
        self.start_worker(self.worker)

    def worker(self):
        x =0
        while self.worker_run:
            self.line=self.AnalogRead()
            time.sleep(self.frec)


    @Pyro4.expose
    def get_line(self):
        return self.line

    def AnalogRead(self):
    	value = [0,0,0,0,0,0]
    	#Read Channel0~channel4 AD values
    	for j in range(0,6):
    		self.GPIO.output(self.CS, LOW)
    		for i in range(0,4):
    			#sent 4-bit Address
    			if(((j) >> (3 - i)) & 0x01):
    				self.GPIO.output(self.Address,HIGH)
    			else:
    				self.GPIO.output(self.Address,LOW)
    			#read MSB 4-bit data
    			value[j] <<= 1
    			if(self.GPIO.input(self.DataOut)):
    				value[j] |= 0x01
    			self.GPIO.output(self.Clock,HIGH)
    			self.GPIO.output(self.Clock,LOW)
    		for i in range(0,6):
    			#read LSB 8-bit data
    			value[j] <<= 1
    			if(self.GPIO.input(self.DataOut)):
    				value[j] |= 0x01
    			self.GPIO.output(self.Clock,HIGH)
    			self.GPIO.output(self.Clock,LOW)
    		#no mean ,just delay
    		for i in range(0,6):
    			self.GPIO.output(self.Clock,HIGH)
    			self.GPIO.output(self.Clock,LOW)
    			time.sleep(0.0001)
    		self.GPIO.output(self.CS,HIGH)
    	return value[1:]
