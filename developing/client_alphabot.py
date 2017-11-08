#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________

import threading
from nodeproxy import clientNODERB
import time
import Pyro4
import cv2
import urllib
import numpy as np

def run_camera(cam):
    while True:
        #c=np.fromstring(cam.image,dtype=np.uint8)
        c1=np.fromstring(cam.image, dtype=np.uint8)
        print type(c1)
        c = cv2.imdecode(c1, -1)
        print type(c)
        #ret,jpeg=cv2.imencode('jpg',c)

        cv2.imshow('alphabot',c1)
        if cv2.waitKey(1) == 27:
            exit(0)

bot=clientNODERB("alphabot@158.49.241.45")
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()

time.sleep(2)
while True:
  pass
