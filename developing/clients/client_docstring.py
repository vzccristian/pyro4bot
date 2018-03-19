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
    bot = ClientRobot("learnbot1")
    # print bot.__dict__
    # print bot.picam.__docstring__()
    # print bot.basemotion.__docstring__()
    print bot.laser.__docstring__()
    print bot.laser.__exposed__()
    #
    # print bot.picam.__exposed__()
    # print bot.picam.__docstring__()
    # bot.node.__docstring__()



    while True:
        time.sleep(0.05)
