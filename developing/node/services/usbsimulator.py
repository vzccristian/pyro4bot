#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from node.libs import control, utils, token
import serial
import simplejson as json
import Pyro4


@Pyro4.expose
class usbsimulator(control.Control):

    __REQUIRED = ["comPort","comPortBaud"]

    @control.load_config
    def __init__(self, data, **kwargs):
        self.buffer = token.Token()
        self.available = 0
        self.lock = 1
        self.IR = [0, 1, 1]
        self.LASER = [0, 0]
        self.init_workers(self.worker_reader)
        #self.init_publisher(self.buffer,)

    def worker_reader(self):
        while self.worker_run:
            self.IR[0]=self.IR[0]+1
            self.LASER[1]=self.LASER[1]+1
            #self.buffer.update_from_dict(self.IR)
            #self.buffer.update_from_dict(self.LASER)
            time.sleep(self.frec)


    @Pyro4.oneway
    def command(self, comman="ee"):
        print comman
        # self.serial.write(comman+"\r\n")


if __name__ == "__main__":
    pass
