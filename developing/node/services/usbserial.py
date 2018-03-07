#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from node.libs import control, utils, token
import serial
import simplejson as json
import Pyro4

"""
JSON_DOCUMENTATION
{SENSOR_NAME} : arduino
{c} cls : usbserial
{c} comPort : /dev/ttyS0
{c} comPortBaud : 115200
{m} frec : 0.02
{m} enable : true
END_JSON_DOCUMENTATION
"""


@Pyro4.expose
class usbserial(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.subscriptors = {}
        self.buffer = token.Token()
        self.writer = []
        self.json = ""
        try:
            self.serial = serial.Serial(
                self.comPort, self.comPortBaud, timeout=3.0)
            if self.serial.isOpen():
                # print(self.serial.name + ' is open..')
                pass
        except Exception:
            print("error usbserial")
            raise
        self.init_workers(self.worker_reader,)
        self.init_publisher(self.buffer,)


    def worker_reader(self):
        self.serial.flushInput()
        while self.worker_run:
            try:
                # print self.serial.read()
                self.json = json.loads(self.read_serial())
                self.buffer.update_from_dict(self.json)
            except Exception:
                #raise
                pass
            time.sleep(self.frec)

    def read_serial(self):
        line = self.serial.readline()
        return line[line.find("{"):line.find("}") + 1]

    @Pyro4.oneway
    def command(self, com="ee"):
        print com
        self.serial.write(com + "\r\n")

    def get__all(self):
        return self.json


if __name__ == "__main__":
    pass
