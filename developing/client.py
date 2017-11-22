#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________

import threading
from nodeproxy import ClientNODERB
import time
import Pyro4
import cv2
import urllib
import numpy as np


def run_camera(cam):
    while True:
        c = cam.image
        cv2.imshow('learnbot', c)
        if cv2.waitKey(1) == 27:
            exit(0)


# nombre del bot en la name no el fichero json
bot = ClientNODERB("learnbot1@158.49.247.170")
cam = threading.Thread(target=run_camera, args=(bot.camera,))
cam.setDaemon(True)
cam.start()

bot.pantilt.barrido(1, 20)
bot.base.set__vel(400, 400)
time.sleep(5)
bot.base.set__vel(0, 0)
while True:
    print bot.laser.get_laser()
    time.sleep(0.05)
