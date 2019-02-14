#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
import time
import datetime
from node.libs import control, utils, token
import serial
import simplejson as json
import Pyro4


class usbsimulator(control.Control):
    __REQUIRED = ["comPort", "comPortBaud"]

    def __init__(self):
        self.buffer = publication.Publication()()
        self.available = 0
        self.lock = 1
        self.IR = [0, 1, 1]
        self.LASER = [0, 0]
        self.start_worker(self.worker_reader)
        self.start_publisher(self.buffer, )

    def worker_reader(self):
        while self.worker_run:
            self.IR[0] = self.IR[0] + 1
            self.LASER[1] = self.LASER[1] + 1
            time.sleep(self.frec)

    @Pyro4.oneway
    def command(self, comman="ee"):
        print(comman)
        # self.serial.write(comman+"\r\n")


if __name__ == "__main__":
    pass
