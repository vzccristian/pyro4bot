#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in you code object
import time
from nodeRBB.LIBS import control
import Pyro4


@Pyro4.expose
class Infrared (control.control):
    @control.loadconfig
    def __init__(self, data, **kwargs):
        # self.arduino.subscribe("IR",self.pyro4id)
        self.send_subscripcion(self.arduino, "IR")
        # this line is the last line in constructor method
        super(Infrared, self).__init__(self.worker)

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)
# here your methods

    def get__ir(self):
        return self.IR

    def get_ir_pon(self):
        irp1 = (self.IR[0] + self.IR[1]) / 20
        irp2 = (self.IR[2] + self.IR[3]) / 20
        return [irp1, irp2]


if __name__ == "__main__":
    pass
