#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ._client_robot import ClientRobot
import time
import Pyro4
import cv2
from urllib import request, parse, error
import numpy as np

SPEED = 1000

bot = ClientRobot("robot_lineas")
# print bot.infrared.__docstring__()
# print bot.basemotion.__docstring__()
bot.basemotion.set__vel(mi=0, md=0)
time.sleep(2)
while True:
    try:
        ir_fixed = [1 if x < 400 else 0 for x in bot.infrared.get__ir()]
        if ir_fixed[3]:
            bot.basemotion.set__vel(SPEED, 0)
        elif ir_fixed[1] or ir_fixed[2]:
            bot.basemotion.set__vel(mi=SPEED, md=SPEED)
        elif ir_fixed[0]:
            bot.basemotion.set__vel(mi=0, md=SPEED)
        else:
            bot.basemotion.set__vel(SPEED, SPEED)
        time.sleep(0.01)
    except:
        pass
