#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from node.libs import control, utils
import serial
import simplejson as json
import Pyro4


@Pyro4.expose
class usbsimulator(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.buffer = [0, 0]
        self.available = 0
        self.lock = 1
        self.IR = [0, 1, 1]
        self.LASER = [0, 0]
        self.init_workers(self.worker_reader)
        self.init_publisher(self.__dict__)


    def worker_reader(self):
        while self.worker_run:
            self.IR[0]=self.IR[0]+1
            self.LASER[1]=self.LASER[1]+1
            time.sleep(self.frec*5)

    def read_serial(self):
        """ esto es el puto comentario"""

        l = self.serial.readline()
        # print l[l.find("{"):l.find("}")+1]
        return l[l.find("{"):l.find("}") + 1]

    @Pyro4.oneway
    def command(self, comman="ee"):
        print comman
        # self.serial.write(comman+"\r\n")


if __name__ == "__main__":
    pass
