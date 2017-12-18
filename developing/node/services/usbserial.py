#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from node.libs import control, utils
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
        self.buffer = [0, 0]
        self.writer = []
        self.available = 0
        self.lock = 1
        try:
            self.serial = serial.Serial(
                self.comPort, self.comPortBaud, timeout=0.05)
            # print self.comPort
            if self.serial.isOpen():
                #print(self.serial.name + ' is open..')
                pass
        except:
                #print("error usbserial")
            raise
        super(usbserial, self).__init__((self.worker_reader, self.worker_dist))

    def worker_reader(self):
        self.serial.flushInput()
        while self.worker_run:
            #print ("usb: %s %s" %(self.available,self.block))
            l = self.serial.readline().split('\r')[0]
            # print l
            try:
                self.buffer[self.lock] = json.loads(self.read_serial())
                self.lock, self.available = self.available, self.lock
            except:
                pass
            time.sleep(self.frec)

    def worker_dist(self):
        while self.worker_run:
            try:
                for k, v in self.subscriptors.iteritems():
                    v.publication(k, self.buffer[self.available][k])
            except:
                #print("USB DIST error: ")
                pass
            time.sleep(self.frec)

    def read_serial(self):
        l = self.serial.readline()
        # print l[l.find("{"):l.find("}")+1]
        return l[l.find("{"):l.find("}") + 1]

    @Pyro4.oneway
    def command(self, comman="ee"):
        print comman
        self.serial.write(comman + "\r\n")


if __name__ == "__main__":
    pass
