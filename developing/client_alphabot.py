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

def track(image):
    blur = cv2.GaussianBlur(image, (5,5),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40,70,70])
    upper_green = np.array([80,200,200])
    lower_pink = np.array([147,95,150])
    upper_pink = np.array([227,255,255])
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    bmask = cv2.GaussianBlur(mask, (5,5),0)
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    ctr = (-1,-1)
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
        cv2.circle(image, ctr, 10, (255,0,0))
    return ctr,image

def run_camera(cam):
    while True:
        c=cam.image
        centro=[]
        centro,img=track(c)
        print centro
        cv2.imshow('learnbot',img)
        if cv2.waitKey(1) == 27:
            exit(0)

bot=clientNODERB("alphabot@192.168.0.165")
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()
bot.base.setMotor(60,60)
bot.base.forward()
time.sleep(2)
bot.base.backward()
time.sleep(2)
bot.base.stop()
bot.base.left()
time.sleep(2)
