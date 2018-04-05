#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4


class RemoteCamera (control.Control):
    # __REQUIRED = ["picambot.picam"]

    def __init__(self):
        for k, v in self.__dict__.iteritems():
            print "K:",k
            print "V:\t",v

        # Worker example
        self.init_workers(self.worker)


        # Subscription example
        #  self.send_subscripcion(self.usbserial, "LASER")

        # Publication example
        # self.buffer = token.Token()
        # self.buffer.update_key_value("value", self.value)
        # self.init_publisher(self.buffer)

    def worker(self):
        while self.worker_run:
            while self._REMOTE_STATUS != "OK":
                self._REMOTE_STATUS
                time.sleep(10)
            print "----------------------------------------------------"
            for k in self.deps.keys():
                print self.deps[k]
            print "----------------------------------------------------"
            time.sleep(self.frec * 500)
            # write here code for your sensor thread

    # here your methods
    # Expose your method to exterior with decorator @Pyro4.expose
    @Pyro4.expose
    def get_value(self):
        return self.value
