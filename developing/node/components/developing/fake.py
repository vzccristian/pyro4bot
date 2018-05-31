#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import pprint

class fake(control.Control):
    __REQUIRED = []
    def __init__(self):
        self.init_workers(self.worker)

        # Publication example
        # self.buffer = token.Token()
        # self.buffer.update_key_value("value", self.value)
        # self.init_publisher(self.buffer)
        # Subscription example
        self.send_subscription("alphabot_apriltag.apriltag", "aprils", "pc_apriltag")

    def worker(self):
        while self.worker_run:
            if hasattr(self, 'aprils'):
                print self.aprils
            time.sleep(10)
            print "--------------------------------------"
            # write here code for your component thread
