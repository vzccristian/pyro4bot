import RPi.GPIO as GPIO
import Pyro4
import smbus

# definitions for RPI.GPIO defs
HIGH = GPIO.HIGH
LOW = GPIO.LOW
IN = GPIO.IN
OUT = GPIO.OUT
BOARD = GPIO.BOARD
BCM = GPIO.BCM
PUD_UP = GPIO.PUD_UP
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
        self.service = gpioservice
        self.__byser = by_service
        try:
            self.mode = self.service.get_mode()
            self.GPIO = GPIO
            self.GPIO.setmode(self.mode)
            self.GPIO.setwarnings(False)
        except:
            return None

    def setup(self,pins,value):
        if self.service.setup(pins,value,self.pyro4id):
            self.GPIO.setup(pins,value)
            return True
        else:
            return False

    def PWM(self,channel,frec):
        return bot_PWM(channel,frec,self.service,self.pyro4id,self.__byser)

    def output(self,pins,value):
        if not self.__byser:
            self.GPIO.output(pins,value)
        else:
            self.service.output(pins,value)

    def input(self,pin):
        if not self.__byser:
            return self.GPIO.input(pin)
        else:
            return self.service.input(pin)

    def add_event_detect(self,channel,when,callback=None,bouncetime=200):
        if not self.__byser:
            self.GPIO.add_event_detect(channel,when,callback,bouncetime)
        else:
            pass

    def add_event_callback(self,channel,callback,bouncetime=200):
        if not self.__byser:
            self.GPIO.add_event_callback(channel,callback,bouncetime)
        else:
            pass

    def remove_event_detect(self,channel):
        if not self.__byser:
            self.GPIO.remove_event_detect(channel)
        else:
            pass

    @property
    def VERSION(self):
        return self.GPIO.VERSION

class bot_PWM(GPIO.PWM):
    def __init__(self,channel,frec,service,pyro4id,byservice = False):
        self.__byser = byservice
        self.service = service
        self.pyro4id = pyro4id
        self.frec = frec
        self.channel = channel
        if not self.__byser:
            super(bot_PWM,self).__init__(channel,frec)
        else:
            #print(channel,self.frec,self.pyro4id)
            self.service.PWM(channel,self.frec,self.pyro4id)

    def start(self,duct):
        if not self.__byser:
            super(bot_PWM,self).start(duct)
        else:
            self.service.start(duct)

    def stop (self):
        if not self.__byser:
            super(bot_PWM,self).stop()
        else:
            self.service.stop(self.channel)

    def remove (self):
        pass

    def ChangeDutyCycle(self,duct):
        if not self.__byser:
            super(bot_PWM,self).ChangeDutyCycle(duct)
        else:
            self.service.ChangeDutyCycle(self.channel,duct)

    def ChangeFrequency(self,frec):
        if not self.__byser:
            super(bot_PWM,self).ChangeFrequency(frec)
        else:
            self.service.ChangeFrequency(self.channel,frec)


class bot_I2C (object):
    def __init__(self,address,i2cservice,pyro4id,by_service):
        self.pyro4id = pyro4id
        self.service = i2cservice
        self.__byser = by_service
