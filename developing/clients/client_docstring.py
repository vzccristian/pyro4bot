#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from _client_robot import ClientRobot
import time
import Pyro4
import cv2
import urllib
import numpy as np
from PIL import Image
import io
import socket
import struct
import time


if __name__ == "__main__":
    print("Ejecutando cliente para docstring...")

    bot = ClientRobot("alphabot_apriltag")
    # print bot.__dict__
    print bot.alphapantilt.__dict__
    while True:
        print "------------"
        pan = raw_input('PAN: ')
        tilt = raw_input('TILT: ')
        try:
            int(pan)
            int(tilt)
            bot.alphapantilt.set_pantilt(pan,tilt)
        except ValueError:
            print "Not a number"
        except Exception:
            raise

    # print bot.picam.__docstring__()
    # print "Infrarred DOC"
    # print bot.infrared.__docstring__()
    # print "Infrarred EXPOSED"
    # print bot.infrared.__exposed__()
    # print "Basemotion DOC"
    # print bot.basemotion.__docstring__()
    # print "Basemotion EXPOSED"
    # print bot.basemotion.__exposed__()
    # print bot.picam.__exposed__()
    # print bot.picam.__docstring__()
    # bot.node.__docstring__()
