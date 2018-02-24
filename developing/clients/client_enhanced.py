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
    start = time.time()
    for i in range(200):
        print i
        #BytesIO
        data = np.fromstring(cam.image.getvalue(), dtype=np.uint8)
        c = cv2.imdecode(data, 1)

        # c.resize(640,480)
        cv2.imshow('learnbot1',c)
        if cv2.waitKey(1) == 27:
           exit(0)
    fin = time.time()
    print ("Time: ", fin-start)

bot=ClientRobot("learnbot1") #nombre del bot en la name no el fichero json
print "Bot adquirido."
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()
bot.pantilt.move(90,110)
time.sleep(2)
# bot.pantilt.barrido(1,20)
# bot.base.Set_Vel(400,400)
# time.sleep(5)
# bot.base.Set_Vel(0,0)
while True:
    #print(bot.pantilt.get_pantilt())
    # print bot.laser.get_laser()
    time.sleep(0.05)
