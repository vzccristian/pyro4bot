#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in you code object
import time
from node.libs import control
import Pyro4



class laser (control.Control):
    __REQUIRED = ["usbserial","LASER","frec"]

    def __init__(self):
        self.init_workers(self.worker)
        self.send_subscripcion(self.usbserial, "LASER")

    def worker(self):
        while self.worker_run:
            # print("LASER-sal:", self.LASER)
            time.sleep(self.frec)
    @Pyro4.expose
    def get_laser(self):
        return self.LASER
