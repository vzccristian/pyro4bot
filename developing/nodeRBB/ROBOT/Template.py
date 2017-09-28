#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
#All datas defined in json configuration are atributes in your code object
import time
from nodeRBB.LIBS import control
import Pyro4

@Pyro4.expose
class <CLASS_NAME>(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):
        #this line is the last line in constructor method
        super(<CLASS_NAME>,self).__init__(self.worker)


    def worker(self):
        while self.worker_run:

            #write here code for your sensor

            time.sleep(self.frec)
#here your methods


if __name__ == "__main__":
    pass
