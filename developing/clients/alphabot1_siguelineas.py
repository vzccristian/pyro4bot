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
time.sleep(3)
print "Working..."
while (True):
    try:
        ir = bot.tlc1543ad.get_line()
        ir_fixed = map(lambda x: 1 if x < 300 else 0,  ir)
        print ir
        print ir_fixed
        # if any(ir_fixed):
        #     V_MAX = 100
        #     V_MIN = 15
        #     minimo = ir.index(min(ir))
        #     n = abs(minimo - len(ir)/2)
        #     if n > 0:
        #         dif_left = ir[minimo - 1] - ir[minimo] if (minimo > 0) else 1000
        #         dif_right = ir[minimo + 1] - ir[minimo] if (minimo < len(ir)-1) else 1000
        #         min_dif = min(dif_left, dif_right) / 10
        #         dif_v = V_MAX - min_dif * n
        #         if dif_left < dif_right:
        #             print "izq"
        #             v_a = abs(V_MAX - dif_v/2)
        #             v_b = abs(V_MIN + dif_v/2)
        #         else:
        #             print "der"
        #             v_b = abs(V_MAX - dif_v/2)
        #             v_a = abs(V_MIN + dif_v/2)
        #         print "min", minimo, "n", n, "dif_left", dif_left, "dif_right", dif_right, "min_dif", min_dif, "dif_v", dif_v, "v_a", v_a, "v_b", v_b
        #     else:
        #             v_b = v_a = V_MAX
        #     print v_a, v_b
        #     bot.l298n.backward(v_a, v_b)
        for i, x in enumerate(ir_fixed):
            if (x):
                if (i == len(ir_fixed)/2):
                    dc_a = dc_b = 90
                elif (i<len(ir_fixed)/2):
                    print "izq"
                    dc_a = 80
                    dc_b = 20
                else:
                    print "der"
                    dc_a = 20
                    dc_b = 80
                bot.l298n.backward(dc_a, dc_b)
    except:
        raise
