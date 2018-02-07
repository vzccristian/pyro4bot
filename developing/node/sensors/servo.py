#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4


@Pyro4.expose
class servo (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.gpioservice.pwm_init(self.PIN,50,self.pyro4id)
        self.gpioservice.pwm_start(self.PIN,7.5)
        time.sleep(2)
        k=0
        for i in range(100):
            self.setangle(4.5+k)
            k=k+0.1
        time.sleep(2)
        self.setangle(10.5)


    def worker(self):
        while self.worker_run:

            time.sleep(self.frec)
            
    def setangle(self,pos=7.5):
        self.gpioservice.pwm_changedutycycle(self.PIN,pos)
        time.sleep(0.5)


if __name__ == "__main__":
    pass
