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
        # c=np.fromstring(cam.image,dtype=np.uint8)
        c = cv2.imdecode(np.fromstring(cam.image, dtype=np.uint8), -1)
        c.resize(320, 240)
        # ret,jpeg=cv2.imencode('jpg',c)

        cv2.imshow('alphabot', c)
        if cv2.waitKey(1) == 27:
            exit(0)


bot = ClientNODERB("alphabot@158.49.241.45")
cam = threading.Thread(target=run_camera, args=(bot.camera,))
cam.setDaemon(True)
cam.start()

time.sleep(2)
while True:
    pass
