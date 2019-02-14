#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All data defined in json configuration are attributes in you code object
import time
from node.libs import control
import Pyro4


class laser(control.Control):
    """Ultrasound sensors through Arduino."""

    __REQUIRED = ["usbserial", "LASER", "frec"]

    def __init__(self):
        # self.start_worker(self.worker)
        self.start_subscription("usbserial", "LASER", "LASER")

    def worker(self):
        while self.worker_run:
            # print("LASER-sal:", self.LASER)
            time.sleep(self.frec)

    @Pyro4.expose
    @control.flask("sensor", 3)
    def get_laser(self):
        return self.LASER
