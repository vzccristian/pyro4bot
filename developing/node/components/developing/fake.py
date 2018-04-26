#!/usr/bin/env python
# -*- coding: utf-8 -*-
# _________collaboration with cristian vazquez____________

import time
from node.libs import control
import sys
import os
import threading
import Pyro4


@Pyro4.expose
class fake(control.Control):

    def __init__(self):
        self.value = 5
        self.init_workers(self.worker)

    def worker(self):
        while self.worker_run:
            print self.value
            self.value += 1
            time.sleep(self.frec * 5)

    @control.flask("sensor", 1)
    def get_value(self):
        print "get_value"
        return self.value

    @control.flask("actuator")
    def set_value(self, value):
        print "set value"
        self.value = value
