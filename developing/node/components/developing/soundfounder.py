#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
from node.libs.gpio import *


class sfline(control.Control):
    """ soundfounder line follower  i2c mode"""
    __REQUIRED = ["i2cservice", "Address", "line"]

    def __init__(self):
        print(self.i2cservice.status)
        self.smbus = bot_I2C(self.Address, self.i2cservice, self.pyro4id)
        print(self.i2cservice.status)

        self.start_worker(self.worker)

    def worker(self):
        while self.worker_run:
            self.line = self.read_analog()
            print(self.line)
            time.sleep(self.frec)

    @Pyro4.expose
    def get_line(self):
        return self.line

    def read_raw(self):
        for i in range(0, 8):
            try:
                raw_result = self.smbus.read_i2c_block_data(self.Address, 0, 10)
                print(raw_result)
                Connection_OK = True
                break
            except:
                print("error")
                Connection_OK = False
        if Connection_OK:
            return raw_result
        else:
            return False

    def read_analog(self):
        raw_result = self.read_raw()
        if raw_result:
            analog_result = [0, 0, 0, 0, 0]
            for i in range(0, 8):
                high_byte = raw_result[i * 2] << 8
                low_byte = raw_result[i * 2 + 1]
                analog_result[i] = high_byte + low_byte
            return analog_result
