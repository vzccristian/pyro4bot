#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
from developing.node.libs.gpio.Platform import HARDWARE

if HARDWARE == "RASPBERRY_PI":
    import RPi.GPIO as GPIO

    # Modes
    BCM = GPIO.BCM
    BOARD = GPIO.BOARD
    UNSET = -1

    # _dir_mapping
    OUT = GPIO.OUT
    IN = GPIO.IN

    HIGH = GPIO.HIGH
    LOW = GPIO.LOW

    # _edge_mapping
    RISING = GPIO.RISING
    FALLING = GPIO.FALLING
    BOTH = GPIO.BOTH

    # _pud_mapping
    PUD_OFF = GPIO.PUD_OFF
    PUD_DOWN = GPIO.PUD_DOWN
    PUD_UP = GPIO.PUD_UP

    modes = {"Unset":-1,
             "BCM":11,
             "BOARD":10
             }

    status = {0:"OUT",
              1:"IN",
              10:"PWM",
              11:"EVENT",
              40:"SERIAL",
              41:"SPI",
              42:"I2C",
              43:"HARD_PWM",
              -1:"UNKNOWN",
              -2:"READ_ERROR",
              -3:"IN USE BY PYRO4BOT OBJECT"
              }

    """ gpioport "is a dict that define 40 phisical pins bus gpio and his correlation with BOARD,BCM and wiringPI
        especifications  pin/BOARD:[decription,BCM,wiringPI]"""
    gpioport={1:["3.3v",None,None], 2:["5v",None,None],
              3:["SDA.1",2,8],      4:["5v",None,None],
              5:["SCL.1",3,9],      6:["0v",None,None],
              7:["GPIO.",4,7],      8:["TxD",14,15],
              9:["0v",None,None],  10:["RxD",15,16],
              11:["GPIO.",17,0],    12:["GPIO.",18,1],
              13:["GPIO.",27,2],    14:["0v",None,None],
              15:["GPIO.",22,3],    16:["GPIO.",23,4],
              17:["3.3v",None,None],18:["GPIO.",24,5],
              19:["MOSI",10,12],    20:["0v",None,None],
              21:["MISO",9,13],     22:["GPIO.",25,6],
              23:["SCLK.",11,14],   24:["CE0",8,10],
              25:["0v",None,None],  26:["CE1",7,18],
              27:["SDA.0",0,30],    28:["SCL.0",1,31],
              29:["GPIO.",5,21],    30:["0v",None,None],
              31:["GPIO.",6,22],    32:["GPIO.",12,26],
              33:["GPIO.",13,23],   34:["0v",None,None],
              35:["GPIO.",19,24],   36:["GPIO.",16,27],
              37:["GPIO.",26,25],   38:["GPIO.",20,28],
              39:["0v",None,None],  40:["GPIO.",21,29],
              }

    max_pwm =20
if HARDWARE == "BEAGLEBONE_BLACK":
    pass
if HARDWARE == "MINNOWBOARD":
    pass
if HARDWARE == "UNKNOWN":
    pass
