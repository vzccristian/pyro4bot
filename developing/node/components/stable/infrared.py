#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in you code object
import time
from node.libs import control
import Pyro4


class infrared (control.Control):
    """Infrared through Arduino."""

    __REQUIRED = ["usbserial", "IR"]

    def __init__(self):
        # self.start_worker(self.worker)
        self.start_subscription("usbserial", "IR")

    def worker(self):
        while self.worker_run:
            # print("IR-sal: ",self.IR)
            time.sleep(self.frec)

    @Pyro4.expose
    @control.flask("sensor", 4)
    def get__ir(self):
        return self.IR

    @Pyro4.expose
    def get_ir_pon(self):
        irp1 = (self.IR[0] + self.IR[1]) / 20
        irp2 = (self.IR[2] + self.IR[3]) / 20
        return [irp1, irp2]


if __name__ == "__main__":
    pass
