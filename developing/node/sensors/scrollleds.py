#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4
import scrollphat

@Pyro4.expose
class scrollleds (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        # this line is the last line in constructor method
        pp=scrollphat.IS31FL3730.IS31FL3730(1)
        super( scrollleds , self).__init__(self.worker)

    def worker(self):
        while self.worker_run:

            # write here code for your sensor

            time.sleep(self.frec)
# here your methods


if __name__ == "__main__":
    pass
