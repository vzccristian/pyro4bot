#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this classes are an adaption of adafruit gpio class
# support three different motherboards
# ____________developed by paco andres____________________
import time
from node.libs.gpio.Platform import *

if HARDWARE == "RASPBERRY_PI":
    import smbus
    if PI_REVISION == 1:
        BUS = 0
    else:
        BUS = 1
    OTHER_BUS = 0 # dtparam=i2c_vc=on PARA ACTIVARLO EN el config de raspaberry

class RPiI2C(object):
    """Class for communicating with an I2C device using the adafruit-pureio pure
    python smbus library, or other smbus compatible I2C interface. Allows reading
    and writing 8-bit, 16-bit, and byte array values to registers
    on the device."""

    def __init__(self, address, service=None, pyro4id=None, bus=None):
        """Create an instance of the I2C device at the specified address on the
        specified I2C bus number."""
        self.address = address
        self.service = service
        self.pyro4id = pyro4id
        try:
            if bus is None:
                self._bus = smbus.SMBus(BUS)
            else:
                self._bus = smbus.SMBus(bus)
            if self.service is not None:
                self.service.register(self.address,self.pyro4id)
        except:
            print(("ERROR: no i2c-{} bus loscated".format(BUS)))

    def detect_ports(self):
        addr = {}
        for device in range(128):
            try:
                print(self._bus.write_byte(device,0))
                addr[device] = []
            except:
                pass
        return addr

    def writeRaw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        value = value & 0xFF
        self._bus.write_byte(self.address, value)


    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        self._bus.write_byte_data(self.address, register, value)
        #print("write8: ",register,value)

    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        value = value & 0xFFFF
        self._bus.write_word_data(self.address, register, value)

    def writeList(self, register, data):
        """Write bytes to the specified register."""
        self._bus.write_i2c_block_data(self.address, register, data)

    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        results = self._bus.read_i2c_block_data(self.address, register, length)
        return results

    def readRaw8(self):
        """Read an 8-bit value on the bus (without register)."""
        result = self._bus.read_byte(self.address) & 0xFF
        return result

    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        result = self._bus.read_byte_data(self.address, register) & 0xFF
        return result

    def readS8(self, register):
        """Read a signed byte from the specified register."""
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self._bus.read_word_data(self.address,register) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(register, little_endian=False)

    def read_byte(self, address):
        """read a single byte from a device, without specifying a device register"""
        try:
            return self._bus.read_byte(address)
        except:
            return None

    def read_data(self, cmd):
        """ read one byte from register cmd """
        try:
            return self._bus.read_byte_data(self.address, cmd)
        except:
            return None

    def read_block_data(self, cmd):
        """ read a block data from register cmd in addresss"""
        try:
            return self._bus.read_block_data(self.address, cmd)
        except:
            return None

    def write_byte(self, data):
        """Send a single byte to a device """
        try:
            self._bus.write_byte(self.address, data)
        except:
            pass

    def write_cmd(self, cmd):
        """Write a single command"""
        try:
            self._bus.write_byte(self.address, cmd)
        except:
            pass

    def write_cmd_arg(self, cmd, data):
        """Write a command and argument"""
        try:
            self._bus.write_byte_data(self.address, cmd, data)
        except:
            pass

    def write_block_data(self, cmd, data):
        """Write a block of data"""
        try:
            self._bus.write_block_data(self.addr, cmd, data)
            time.sleep(0.0001)
        except:
            pass

if HARDWARE == "RASPBERRY_PI":
    I2CCLS = RPiI2C
