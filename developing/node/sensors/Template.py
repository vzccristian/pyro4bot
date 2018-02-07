#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control
import Pyro4


@Pyro4.expose
class < CLASS_NAME > (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        #self.init_workers(self.worker)
        #self.init_publisher(self.__dict__)

    def worker(self):
        while self.worker_run:

            # write here code for your sensor

            time.sleep(self.frec)
# here your methods


if __name__ == "__main__":
    pass
