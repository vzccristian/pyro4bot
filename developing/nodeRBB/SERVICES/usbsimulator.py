#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from nodeRBB.LIBS import control, utils
import serial
import simplejson as json
import Pyro4


@Pyro4.expose
class UsbSimulator(control.control):
    @control.loadconfig
    def __init__(self, data, **kwargs):
        self.subscriptors = {}
        self.buffer = [0, 0]
        self.available = 0
        self.lock = 1

        super(UsbSimulator, self).__init__(
            (self.worker_reader, self.worker_dist))

    def worker_reader(self):
        while self.worker_run:
            time.sleep(self.frec)

    def worker_dist(self):
        while self.worker_run:

            time.sleep(self.frec)

    def read_serial(self):
        l = self.serial.readline()
        # print l[l.find("{"):l.find("}")+1]
        return l[l.find("{"):l.find("}") + 1]

    @Pyro4.oneway
    def command(self, comman="ee"):
        print comman
        # self.serial.write(comman+"\r\n")


if __name__ == "__main__":
    pass
