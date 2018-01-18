#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object

import time
from node.libs import control
import Pyro4
import smbus
BUS = 1


@Pyro4.expose
class i2cservice (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.bus = smbus.SMBus(BUS)
        self.gpioservice.i2c_setup(self.pyro4id)
        self.addr = {}
        self.detect_ports()
        print ("I2C:",self.status())

        # this line is the last line in constructor method
        super(i2cservice, self).__init__(self.worker)

    def worker(self):
        pass

    def status(self):
        return self.addr

    def detect_ports(self):
        for device in range(128):
            try:
                print self.bus.write_byte(device,0)
                self.addr[device] = []
            except:
                pass

    def register(self, address, proxy):
        """register a proxy in a one address device"""
        if address in self.addr:
            self.addr[address].append(proxy)
            return True
        else:
            return False

    def read_byte(self, address):
        """read a single byte from a device, without specifying a device register"""
        try:
            return self.bus.read_byte(address)
            time.sleep(0.0001)
        except:
            return None

    def read_data(self, address, cmd):
        """ read one byte from register cmd """
        try:
            return self.bus.read_byte_data(address, cmd)
            time.sleep(0.0001)
        except:
            return None

    def read_block_data(self, address, cmd):
        """ read a block data from register cmd in addresss"""
        try:
            return self.bus.read_block_data(address, cmd)
            time.sleep(0.0001)
        except:
            return None

    def write_byte(self, address, data):
        """Send a single byte to a device """
        try:
            self.i2c.write_byte(address, data)
        except:
            pass

    def write_cmd(self, address, cmd):
        """Write a single command"""
        try:
            self.bus.write_byte(address, cmd)
            time.sleep(0.0001)
        except:
            pass

    def write_cmd_arg(self, address, cmd, data):
        """Write a command and argument"""
        try:
            self.bus.write_byte_data(address, cmd, data)
            time.sleep(0.0001)
        except:
            pass

    def write_block_data(self, cmd, data):
        """Write a block of data"""
        try:
            self.bus.write_block_data(self.addr, cmd, data)
            time.sleep(0.0001)
        except:
            pass


if __name__ == "__main__":
    pass
