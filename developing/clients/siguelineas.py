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

SPEED = 1000

bot = ClientRobot("robot_lineas")
print("Bot adquirido...")
# bot.pantilt.move(90, 120)
# print bot.infrared.__docstring__()
# print bot.basemotion.__docstring__()
bot.basemotion.set__vel(mi=0,md=0)
time.sleep(2)
while (True):
    try:
        ir =  bot.infrared.get__ir()
        print ir
        ir_fixed = map(lambda x: 1 if x < 200 else 0, ir)
        print ir_fixed
        if ir_fixed[0]:
            print "izq"
            bot.basemotion.set__vel(mi=0,md=SPEED)
        elif (ir_fixed[1] or ir_fixed[2]):
            print "recto"
            bot.basemotion.set__vel(mi=SPEED,md=SPEED)
        elif ir_fixed[3]:
            print "der"
            bot.basemotion.set__vel(SPEED,0)
        else:
            print "otro_recto"
            bot.basemotion.set__vel(SPEED,SPEED)
        time.sleep(0.01)
    except:
        pass
    # bot.basemotion.set__vel(mi=0,md=0)
print("Saliendo...")
