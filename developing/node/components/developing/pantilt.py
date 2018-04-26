#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
import time
from node.libs import control, utils
import Pyro4

@Pyro4.expose
class pantilt(control.Control):

    __REQUIRED = ["usbserial","PT"]

    def __init__(self):
        self.send_subscripcion(self.usbserial, "PT")
        self.bar = False
        self.ptblock = False
        self.init_workers(self.worker)
        #print(self.node.get_uris())
    def worker(self):
        while self.worker_run:
            # write here code for your component
            time.sleep(self.frec)

    @Pyro4.oneway
    @control.flask("actuator")
    def move(self, pan=90, tilt=90):
        if self.ptblock == False:
            self.usbserial.command("setpt " + str(pan) + "," + str(tilt))
            while self.PT[0] != pan and self.PT[1] != tilt:
                print "wait servo"
                self.ptblock = True
            self.ptblock = False

    @Pyro4.oneway
    @control.flask("actuator")
    def barrido(self, i, f):
        if not self.bar:
            self.bar = True
            for l in range(i, f, 1):
                self.move(l, 120)
                time.sleep(0.05)
            self.bar = False

    @control.flask("sensor", 2)
    def get_pantilt(self):
        return self.PT


if __name__ == "__main__":
    pass
