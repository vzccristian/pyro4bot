#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in you code object
import time
from node.libs import control
import Pyro4

"""
JSON_DOCUMENTATION
{SENSOR_NAME} : infrared
{c} cls : infrared
{m} IR : [0,0,0,0]
{d} --> : ["arduino"]
{m} enable : true
{m} worker_run : true
{m} frec : 0.02
END_JSON_DOCUMENTATION
"""

class infrared (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.init_workers(self.worker)
        self.send_subscripcion(self.arduino, "IR")

    def worker(self):
        while self.worker_run:
            #print("salida: ",self.IR)
            time.sleep(self.frec)


    @Pyro4.expose
    def get__ir(self):
        return self.IR

    @Pyro4.expose
    def get_ir_pon(self):
        irp1 = (self.IR[0] + self.IR[1]) / 20
        irp2 = (self.IR[2] + self.IR[3]) / 20
        return [irp1, irp2]


if __name__ == "__main__":
    pass
