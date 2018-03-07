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

bot = ClientRobot("alphabot_linea")
# print bot.infrared.__docstring__()
# print bot.basemotion.__docstring__()
bot.l298n.stop()
while (True):
    try:
        ir_fixed = map(lambda x: 1 if x < 400 else 0,  bot.tlc1543ad.get_line())
        # print ir_fixed
        for i, x in enumerate(ir_fixed):
            if (x):
                if (i == len(ir_fixed)/2):
                    dc_a = dc_b = 100
                elif (i<len(ir_fixed)/2):
                    dc_a = 300
                    dc_b = 20
                else:
                    dc_a = 20
                    dc_b = 300
                bot.l298n.backward(dc_a,dc_b)
    except:
        raise
