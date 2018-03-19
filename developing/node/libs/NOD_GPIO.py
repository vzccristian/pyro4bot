import RPi.GPIO as GPIO
import Pyro4


class NOD_GPIO(object):

    def __init__(self,gpioservice,pyro4id,by_service=False):
        self.pyro4id = pyro4id
        self.gpioservice = gpioservice
        self.mode =gpioservice.get_mode()
        if by_service:
            self.GPIO=gpio_service if by_service else self.GPIO=GPIO
