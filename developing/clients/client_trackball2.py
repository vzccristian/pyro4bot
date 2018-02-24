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
from PIL import Image
import io

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

def run_camera(cam,pantilt,base):
    while True:
        c=cam.image
        c = np.array(c)
        c = c[:, :, ::-1].copy()
        centro=[]
        centro,img=track(c)
        print centro
        cv2.imshow('learnbot',img)
        pt =  pantilt.get_pantilt()

        if cv2.waitKey(1) == 27:
            exit(0)
        # if (centro[0]>0 and centro[0]<50):
        #     for i in xrange(0,20,+1):
        #         print ("1:",i, "POS:",pantilt.get_pantilt())
        #         base.Set_Vel(0,100)
        #         pantilt.move(pt[0]-i,pt[1])
        #         time.sleep(0.01)
        #         base.Set_Vel(0,0)
        # elif (centro[0]>320-50 and centro[0]<320):
        #     for i in xrange(0,20,+1):
        #         print ("2:",i, "POS:",pantilt.get_pantilt())
        #         base.Set_Vel(100,00)
        #         pantilt.move(pt[0]+i,pt[1])
        #         time.sleep(0.01)
        #         base.Set_Vel(0,0)
        # elif (centro[1]>0 and centro[1]<50):
        #     for i in xrange(0,20,+1):
        #         print ("3:",i, "POS:",pantilt.get_pantilt())
        #         pantilt.move(pt[0],pt[1]+i)
        #         time.sleep(0.01)
        # elif (centro[1]>240-50 and centro[1]<240):
        #     for i in xrange(0,20,+1):
        #         print ("4:",i, "POS:",pantilt.get_pantilt())
        #         pantilt.move(pt[0],pt[1]-i)
        #         time.sleep(0.01)
        # elif (centro[1]<240-100 and centro[1]>100) and (centro[0]<320-100 and centro[0]>100):
        #     if (pt[0]<90): #izquierda
        #         base.Set_Vel(0,100)
        #     else: #derecha
        #         base.Set_Vel(100,0)
        #     time.sleep(0.01)
        #     base.Set_Vel(0,0)
        # elif (pt[1]<240-100 and pt[1]>100) and (pt[0]<320-100 and pt[0]>100):
        #         base.Set_Vel(500,500)
        #         time.sleep(1)
        #         base.Set_Vel(0,0)

def run_camera2(cam):
    print ("run_camera2")
    while (True):
        img = cam.image
        # if (img.size.width > 0 and img.size.height> 0):
        cv2.imshow('learnbot',img)
        # else:
            # print ("Imagen vacia")
        if cv2.waitKey(1) == 27:
            exit(0)


#bot=ClientRobot("simplebot@158.49.241.68") #nombre del bot en la name no el fichero json
bot=ClientRobot("learnbot1")
print ("BOT adquirido.")
bot.pantilt.move(90,110)
cam=threading.Thread(target=run_camera,args=(bot.camera,bot.pantilt,bot.base,))
cam.setDaemon(True)
cam.start()

#TEST CABEZA
# for i in xrange (90,150,+2):
#     print (i)
#     bot.pantilt.move(90,i)
#     time.sleep(0.1)
# time.sleep(1)
# for i in xrange (150,110,-2):
#     print (i)
#     bot.pantilt.move(90,i)
#     time.sleep(0.1)

#bot.pantilt.move(90,120)

# for i in range(1,5000):
#     print ("ir pon: %s infrared: %s" % (bot.infrared.get_IR_pon(),bot.infrared.get_IR()))
#     time.sleep(1)
# bot.base.Set_Vel(0,0)
# bot.base.Set_Vel(1000,1000)
# time.sleep(2)
# bot.base.Set_Vel(0,0)
# bot.base.Set_Vel(000,500)
# time.sleep(5)
# bot.base.Set_Vel(0,0)
while True:
    pass
