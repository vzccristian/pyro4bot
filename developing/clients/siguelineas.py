#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________

import threading
from _client_robot import ClientRobot
import time
import Pyro4
import cv2
import urllib
import numpy as np


def run_camera(cam):
    while True:
        c = cam.image
        #gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
        cv2.imshow('learnbot', c)
        if cv2.waitKey(1) == 27:
            exit(0)


# nombre del bot en la name no el fichero json
bot = ClientRobot("learnbot1@192.168.1.37")
cam = threading.Thread(target=run_camera, args=(bot.camera,))
cam.setDaemon(True)
cam.start()
bot.pantilt.move(90, 120)
for i in range(1, 1000):
    print("ir:%s" % (bot.infrared.get_ir()))
bot.base.set__vel(0, 0)
bot.pantilt.move(90, 120)
while True:
    pass
