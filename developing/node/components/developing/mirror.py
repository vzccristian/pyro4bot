#!/usr/bin/env python
# ____________developed by cristian vazque____________________
# _________collaboration with cristian vazquez____________

import time
from node.libs import control
import pprint
import Pyro4

class mirror(control.Control):
    def __init__(self):
        self.init_workers(self.worker)

    def worker(self):
        print("MIRROR WORKING")
        # print(self.deps["esclavo.ruedas"].__docstring__())
        # while self.worker_run:
        #     time.sleep(self.frec)

    @Pyro4.expose
    @Pyro4.oneway
    @control.flask("actuator")
    def set__vel(self, mi=1000, md=1000):
        try:
            if (mi>100): mi=100
            elif (mi<-100): mi=-100
            if (md>100): md=100
            elif (md<-100): md=-100
            self.init_thread(self.deps["esclavo.ruedas"].setvel, mi, md)
        except Exception:
            print("Error mirroring")

        # self.usbserial.command(com="base " + str(mi) + "," + str(md))
