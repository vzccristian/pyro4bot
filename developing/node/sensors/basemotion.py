#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
from node.libs import control, utils
import Pyro4

"""
JSON_DOCUMENTATION
{SENSOR_NAME} : base
{c} cls : basemotion
{m} BASE : [0,0]
{d} --> : ["arduino"]
{m} enable : true
{m} worker_run : true
{m} frec : 0.03
END_JSON_DOCUMENTATION
"""

@Pyro4.expose
class basemotion(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        # print self.__dict__
        self.send_subscripcion(self.arduino, "BASE")
        super(basemotion, self).__init__(self.worker)
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
