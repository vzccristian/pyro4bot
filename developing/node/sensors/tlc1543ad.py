#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import RPi.GPIO as GPIO


class tlc1543ad (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.gpioservice.setup((self.Clock,self.Address,self.CS),GPIO.OUT,self.pyro4id)
        self.gpioservice.setup(self.DataOut,GPIO.IN,self.pyro4id)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.Clock,GPIO.OUT)
        GPIO.setup(self.Address,GPIO.OUT)
        GPIO.setup(self.CS,GPIO.OUT)
        GPIO.setup(self.DataOut,GPIO.IN,GPIO.PUD_UP)
        self.init_workers(self.worker)

        # Subscription example
        #  self.send_subscripcion(self.arduino, "LASER")

        # Publication example
        # self.buffer = token.Token()
        # self.buffer.update_key_value("value", self.value)
        # self.init_publisher(self.buffer)

    def worker(self):
        while self.worker_run:
            self.line=self.AnalogRead()
            #print(self.line)

    @Pyro4.expose
    def get_line(self):
        return self.line
    def AnalogRead(self):
    	value = [0,0,0,0,0,0]
    	#Read Channel0~channel4 AD value
    	for j in range(0,6):
    		GPIO.output(self.CS, GPIO.LOW)
    		for i in range(0,4):
    			#sent 4-bit Address
    			if(((j) >> (3 - i)) & 0x01):
    				GPIO.output(self.Address,GPIO.HIGH)
    			else:
    				GPIO.output(self.Address,GPIO.LOW)
    			#read MSB 4-bit data
    			value[j] <<= 1
    			if(GPIO.input(self.DataOut)):
    				value[j] |= 0x01        #GPIO.setup(DataOut,GPIO.IN,GPIO.PUD_UP)
    			GPIO.output(self.Clock,GPIO.HIGH)
    			GPIO.output(self.Clock,GPIO.LOW)
    		for i in range(0,6):
    			#read LSB 8-bit data
    			value[j] <<= 1
    			if(GPIO.input(self.DataOut)):
    				value[j] |= 0x01
    			GPIO.output(self.Clock,GPIO.HIGH)
    			GPIO.output(self.Clock,GPIO.LOW)
    		#no mean ,just delay
    		for i in range(0,6):
    			GPIO.output(self.Clock,GPIO.HIGH)
    			GPIO.output(self.Clock,GPIO.LOW)
    			time.sleep(0.0001)
    		GPIO.output(self.CS,GPIO.HIGH)
    	return value[1:]
