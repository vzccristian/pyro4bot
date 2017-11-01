#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
#All datas defined in json configuration are atributes in your code object
import time
from nodeRBB.LIBS import control
import Pyro4
<<<<<<< HEAD
import RPi.GPIO as GPIO
=======
>>>>>>> 9bbd43bfb06c3c1c16568ee7672a5ae35ea7184f

@Pyro4.expose
class gpioservice(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):
<<<<<<< HEAD
        
        GPIO.setmode(self.mode)
        GPIO.setwarnings(False)
=======
>>>>>>> 9bbd43bfb06c3c1c16568ee7672a5ae35ea7184f
        #this line is the last line in constructor method
        super(gpioservice,self).__init__(self.worker)


    def worker(self):
        while self.worker_run:

            #write here code for your sensor

            time.sleep(self.frec)
#here your methods


if __name__ == "__main__":
    pass
