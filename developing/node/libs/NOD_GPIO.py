import RPi.GPIO as GPIO
import Pyro4


class NOD_GPIO(object):

    def __init__(self,pyro4id,gpio_service=None,by_service=False):
        if by_service:
            self.GPIO=gpio_service if by_service else self.GPIO=GPIO
