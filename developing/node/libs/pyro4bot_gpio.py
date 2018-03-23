import RPi.GPIO as GPIO
import Pyro4
from smbus import SMBus

# definitions for RPI.GPIO defs
HIGH = GPIO.HIGH
LOW = GPIO.LOW
IN = GPIO.IN
OUT = GPIO.OUT
BOARD = GPIO.BOARD
BCM = GPIO.BCM
PUD_UP = GPIO.PUD_UP
PUD_DOWN = GPIO.PUD_DOWN
RISING = GPIO.RISING
FALLING = GPIO.FALLING
BOTH = GPIO.BOTH

# definitions for SMBus
BUS = 1

class bot_GPIO(object):
    """
     This class is a wrapper for RPI.GPIO and gpioservice
     All sensors and other services must be use this wrapper to access
     to gpio port
    """
    def __init__(self,gpioservice,pyro4id,by_service=False):
        self.pyro4id = pyro4id
        self.SGPIO = gpioservice
        self.HGPIO = GPIO
        self.__byser = by_service
        self.GPIO = self.SGPIO if by_service else self.HGPIO

        try:
            self.mode = self.SGPIO.get_mode()
            self.HGPIO.setmode(self.mode)
            self.HGPIO.setwarnings(False)
        except:
            return None

    def setup(self,pins,*value):
        if not self.__byser:
            self.HGPIO.setup(pins,*value)
        return self.SGPIO.setup(pins,self.pyro4id,*value)

    def PWM(self,channel,frec):
        return bot_PWM(channel,frec,self.SGPIO,self.pyro4id,self.__byser)

    def output(self,pins,value):
        self.GPIO.output(pins,value)

    def input(self,pin):
        return self.GPIO.input(pin)

    def add_event_detect(self,channel,when,callback=None,bouncetime=200):
        self.HGPIO.add_event_detect(channel,when,callback,bouncetime)

    def add_event_callback(self,channel,callback,bouncetime=200):
        self.HGPIO.add_event_callback(channel,callback,bouncetime)

    def remove_event_detect(self,channel):
        self.HGPIO.remove_event_detect(channel)

    @property
    def VERSION(self):
        return self.GPIO.VERSION

    @property
    def STATUS(self):
        return self.SGPIO.status()

class bot_PWM(object):
    def __init__(self,channel,frec,service,pyro4id,byservice = False):
        self.__byser = byservice
        self.service = service
        self.pyro4id = pyro4id
        self.frec = frec
        self.channel = channel
        if not self.__byser:
            self.PWM = GPIO.PWM(channel,frec)
        else:
            #print(channel,self.frec,self.pyro4id)
            self.PWM = self.service.PWM(channel,self.frec,self.pyro4id)

    def start(self,duct):
        self.PWM.start(self.channel,duct) if self.__byser else self.PWM.start(duct)

    def stop (self):
        self.PWM.stop(self.channel,duct) if self.__byser else self.PWM.stop(duct)

    def remove (self):
        pass

    def ChangeDutyCycle(self,duct):
        self.PWM.ChangeDutyCycle(self.channel,duct) if self.__byser else self.PWM.ChangeDutyCycle(duct)

    def ChangeFrequency(self,frec):
        self.PWM.ChangeFrequency(self.channel,duct) if self.__byser else self.PWM.ChangeFrequency(duct)


class bot_I2C (object):
    def __init__(self,address,i2cservice,pyro4id,by_service=False):
        self.pyro4id = pyro4id
        self.service = i2cservice
        self.bus = self.service.BUS
        self.__byser = by_service
        if self.service.register(address,self.pyro4id):
            try:
                self.smbus = SMBus(self.bus)
            except:
                print("ERROR: no i2c-{} bus located".format(BUS))
        else:
            print("ERROR:I2C address not regitered")

    def read_byte(self, address):
        """read a single byte from a device, without specifying a device register"""
        try:
            return self.smbus.read_byte(address)
        except:
            return None

    def read_data(self, address, cmd):
        """ read one byte from register cmd """
        try:
            return self.smbus.read_byte_data(address, cmd)
        except:
            return None

    def read_block_data(self, address, cmd):
        """ read a block data from register cmd in addresss"""
        try:
            return self.smbus.read_block_data(address, cmd)
        except:
            return None

    def write_byte(self, address, data):
        """Send a single byte to a device """
        try:
            self.smbus.write_byte(address, data)
        except:
            pass

    def write_cmd(self, address, cmd):
        """Write a single command"""
        try:
            self.smbus.write_byte(address, cmd)
        except:
            pass

    def write_cmd_arg(self, address, cmd, data):
        """Write a command and argument"""
        try:
            self.smbus.write_byte_data(address, cmd, data)
        except:
            pass

    def write_block_data(self, cmd, data):
        """Write a block of data"""
        try:
            self.smbus.write_block_data(self.addr, cmd, data)
        except:
            pass
