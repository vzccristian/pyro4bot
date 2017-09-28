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
    lower_green = np.array([29,86,6])
    upper_green = np.array([64,255,255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
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
        #print centro
        cv2.imshow('learnbot',img)
        if cv2.waitKey(1) == 27:
            exit(0)

bot=clientNODERB("learnbot1@192.168.1.40") #nombre del bot en la name no el fichero json
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()
bot.base.Set_Vel(-600,-600)
time.sleep(5)
bot.base.Set_Vel(0,0)

bot.pantilt.move(80,160)
for i in range(1,200):
    laser=bot.laser.get_laser()
    mx=max(laser)
    ind=laser.index(mx)
    print ("laser:%s ind:%s" % (laser,ind))
    if ind==0:
        #bot.base.Set_Vel(300,100)
        print "izquierda"
    if ind==1:
        #bot.base.Set_Vel(200,200)
        print "centro"
    if ind==2:
        #bot.base.Set_Vel(100,300)
        print "derecha"
    time.sleep(0.1)

bot.base.Set_Vel(0,0)
while True:
    pass
