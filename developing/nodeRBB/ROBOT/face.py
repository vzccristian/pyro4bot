#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
import time
from nodeRBB.LIBS import control,utils
import Pyro4


@Pyro4.expose
class face(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):

        super(face,self).__init__(self.worker)

    def worker(self):
        while self.worker_run:
            #write here code for your sensor
            time.sleep(self.frec)

    

if __name__ == "__main__":
    pass
