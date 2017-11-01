#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
#All datas defined in json configuration are atributes in your code object
import time
from nodeRBB.LIBS import control
import Pyro4
import RPi.GPIO as GPIO
modes = {-1:"Unset", 11:"BCM", 10:"BOARD"}
#BCM is a dict for control pyros working with gpio port:[use,pinboard,IN/OUT,Proxy]
BCM={1:["id_sc",28,None,None],2:["sda",3,None,None],3:["scl",5,None,None],4:["gpclk",7,None,None],
     5:["--",29,None,None],6:["--",31,None,None],7:["CE1",26,None,None],8:["CE0",25,None,None],
     9:["MISO",21,None,None],10:["MOSI",19,None,None],11:["sclk",23,None,None],12:["pwm0",32,None,None],
     13:["PWM1",33,None,None],14:["TXD",8,None,None],15:["RXD",10,None,None],16:["--",36,None,None],
     17:["--",11,None,None],18:["PWM0",12,None,None],19:["MISO",35,None,None],20:["MOSI",38,None,None],
     21:["SCLK",40,None,None],22:["--",15,None,None],23:["--",16,None,None],24:["--",18,None,None],
     25:["--",22,None,None],26:["--",37,None,None]}
BOARD={k:[k,"--",None,None] for k in range(1,40) }

@Pyro4.expose
class gpioservice(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):
        GPIO.setmode(self.mode)
        GPIO.setwarnings(False)
        if self.mode==11:
            self.GPIO=BCM
        else:
            self.GPIO=BOARD

        #this line is the last line in constructor method
        super(gpioservice,self).__init__(self.worker)
    def worker(self):
        pass
#here your methods
    def status(self):
      return self.GPIO
  
    def setup(self,pins,value,proxy):
       """set pins in service gpio with initial value"""
       if type(pins)==list:
           for k in pins:
               if self.GPIO.has_key(k):
                   self.GPIO[k][2]=value
                   self.GPIO[k][3]=proxy
                   GPIO.setup(k,value)
       else:
           if self.GPIO.has_key(pins):
               self.GPIO[pins][2]=value
               self.GPIO[pins][3]=proxy
               GPIO.setup(pins,value)

    def get_mode(self):
        """ Return mode bcm 11 or BOARD 10 active"""
        return modes[GPIO.getmode()]
    def set_mode(self,m=11):
        """ Set mode 11 BCM 10 BOARD """
        self.mode=m
        GPIO.setmode(self.mode)

if __name__ == "__main__":
    pass
