#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
from nodeRBB.LIBS import control, utils
import Pyro4


@Pyro4.expose
class Basemotion(control.control):
    @control.loadconfig
    def __init__(self, data, **kwargs):
        # print self.__dict__
        self.send_subscripcion(self.arduino, "BASE")
        super(Basemotion, self).__init__(self.worker)
        # self.Set_Vel(0,0)
        # print self.__dict__

    def worker(self):
        while self.worker_run:
            # write here code for your sensor
            time.sleep(self.frec)

    @Pyro4.oneway
    def set__vel(self, mi=1, md=1):
        self.arduino.command("base " + str(mi) + "," + str(md))

    def get_base(self):
        return self.BASE


if __name__ == "__main__":
    pass
