#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
import time
from node.libs import control
import Pyro4

@Pyro4.expose
class face(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.init_workers(self.worker)
        # print self.__dict__
        # print self.suelo.get__ir()

    def worker(self):
        while self.worker_run:
            # write here code for your sensor
            time.sleep(self.frec)


if __name__ == "__main__":
    pass
