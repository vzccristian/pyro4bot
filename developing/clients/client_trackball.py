#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________

import threading
from ._client_robot import ClientRobot
import time
import Pyro4
import cv2
from urllib import request, parse, error
import numpy as np


def track(image):
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 200, 200])
    lower_pink = np.array([147, 95, 150])
    upper_pink = np.array([227, 255, 255])
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    ctr = (-1,-1)
    if centroid_x is not None and centroid_y is not None:
        ctr = (centroid_x, centroid_y)
        cv2.circle(image, ctr, 10, (255, 0, 0))
    return ctr,image


def run_camera(cam):
    while True:
        c = cam.image
        centro = []
        centro, img = track(c)
        print(centro)
        cv2.imshow('learnbot', img)
        if cv2.waitKey(1) == 27:
            exit(0)

# bot=ClientRobot("simplebot@158.49.241.68") #nombre del bot en la name no el fichero json


bot = ClientRobot("learnbot1")
cam = threading.Thread(target=run_camera, args=(bot.camera,))
cam.setDaemon(True)
cam.start()
time.sleep(2)

# TEST CABEZA
# for i in xrange (90,150,+2):
#     print (i)
#     bot.pantilt.move(90,i)
#     time.sleep(0.1)
# time.sleep(1)
# for i in xrange (150,110,-2):
#     print (i)
#     bot.pantilt.move(90,i)
#     time.sleep(0.1)

# bot.pantilt.move(90,120)

# for i in range(1,5000):
#     print ("ir pon: %s infrared: %s" % (bot.infrared.get_IR_pon(),bot.infrared.get_IR()))
#     time.sleep(1)
bot.base.Set_Vel(0, 0)
bot.base.Set_Vel(1000, 1000)
time.sleep(2)
bot.base.Set_Vel(0, 0)
bot.base.Set_Vel(000, 500)
time.sleep(5)
bot.base.Set_Vel(0, 0)
while True:
    pass
