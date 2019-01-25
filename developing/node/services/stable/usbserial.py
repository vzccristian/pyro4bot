#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
import time
from node.libs import control, subscription, publication
import serial
import json
import Pyro4


@Pyro4.expose
class usbserial(control.Control):
    __REQUIRED = ["comPort", "comPortBaud"]

    def __init__(self):
        # self.subscriptors = {}
        self.buffer = publication.Publication()
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
        self.start_worker(self.worker_reader, )
        self.start_publisher(self.buffer, )

    def worker_reader(self):
        self.serial.flushInput()
        while self.worker_run:
            try:
                self.json = json.loads(self.read_serial())
                self.buffer.update_from_dict(self.json)
            except Exception:
                # raise
                pass
            time.sleep(self.frec)

    def read_serial(self):
        line = self.serial.readline()
        return line[line.find("{"):line.find("}") + 1]

    @Pyro4.oneway
    def command(self, com="ee"):
        # print(com)
        self.serial.write((com + "\r\n").encode())

    def get__all(self):
        return self.json
