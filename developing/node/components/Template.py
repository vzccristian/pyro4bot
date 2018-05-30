#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4


class ClassName (control.Control):
    __REQUIRED = []
    def __init__(self):
        # Atribute example
        self.value = 0

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
            # write here code for your component thread

    #  here your methods
    #  Expose your method to exterior with decorator @Pyro4.expose
    @Pyro4.expose
    def get_value(self):
        return self.value
