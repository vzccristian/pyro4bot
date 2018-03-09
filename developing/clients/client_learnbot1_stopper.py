#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _client_robot import ClientRobot
import time
import threading
from random import randint

SPEED = 1000

def check_infrarred(bot):
    movimiento = True
    ir_fixed = map(lambda x: 1 if x < 200 else 0, bot.infrared.get__ir())
    while(ir_fixed[3] or ir_fixed[2] or ir_fixed[1] or ir_fixed[0]):
        movimiento = False
        print "Infrarred", ir_fixed
        mov(bot, -SPEED, -SPEED, 3)
        movRandom(bot, -SPEED, 3)
        mov(bot, 0, 0, 0)
        ir_fixed = map(lambda x: 1 if x < 200 else 0, bot.infrared.get__ir())
    return movimiento

def movRandom(bot, speed=SPEED, t=1):
    print "movRANDOM"
    if randint(0, 1) == 1:
        bot.basemotion.set__vel(mi=speed, md=0)
    else:
        bot.basemotion.set__vel(mi=0, md=speed)
    time.sleep(t)


def mov(bot, a_speed=SPEED, b_speed=SPEED, t=1):
    bot.basemotion.set__vel(mi=a_speed, md=b_speed)
    time.sleep(t)


def run(bot):
    movimiento = False
    mov(bot, SPEED, SPEED, 0.2)
    while (True):
        print movimiento
        movimiento = check_infrarred(bot)
        laser = bot.laser.get_laser()
        print "Laser", laser
        laser_fixed = map(lambda x: 1 if x < 110 else 0, laser)
        if laser_fixed[1]:
            print "izq"
            mov(bot, 0, 0, 0)
            mov(bot, -SPEED, -SPEED, 1)
            mov(bot, 0, -SPEED, 1)
            movimiento = False
        elif laser_fixed[0]:
            print "centr"
            mov(bot, 0, 0, 0)
            mov(bot, -SPEED, -SPEED, 1)
            movRandom(bot, -SPEED, 1)
            movimiento = False
        elif laser_fixed[2]:
            print "der"
            mov(bot, 0, 0, 0)
            mov(bot, -SPEED, -SPEED, 1)
            mov(bot, -SPEED, 0, 1)
            movimiento = False
        print movimiento
        if not (movimiento):
            mov(bot, SPEED, SPEED, 0.2)
            movimiento = True

if __name__ == '__main__':
    bot = ClientRobot("learnbot1_stopper")
    mov(bot, 0, 0, 2)
    try:
        run(bot)
    except Exception:
        print "error"
        mov(bot, 0, 0, 0)
