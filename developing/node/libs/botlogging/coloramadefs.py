#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________
from colorama import Cursor, init, Fore, Back, Style
import re

init()
STYLE = re.compile("\[[F,B,S][A-Z]\]")
print(Style.RESET_ALL)

color = {"[FR]": Fore.RED,
         "[FY]": Fore.YELLOW,
         "[FB]": Fore.BLUE,
         "[FG]": Fore.GREEN,
         "[FM]": Fore.MAGENTA,
         "[FC]": Fore.CYAN,
         "[FW]": Fore.WHITE,
         "[FN]": Fore.BLACK,
         "[FS]": Fore.RESET,
         "[BB]": Back.BLUE,
         "[BR]": Back.RED,
         "[BG]": Back.GREEN,
         "[BY]": Back.YELLOW,
         "[BM]": Back.MAGENTA,
         "[BC]": Back.CYAN,
         "[BW]": Back.WHITE,
         "[BS]": Back.RESET,
         "[SD]": Style.DIM,
         "[SN]": Style.NORMAL,
         "[SB]": Style.BRIGHT,
         "[SR]": Style.RESET_ALL
         }


def pos(x, y):
    return Cursor.POS(x, y)


def up(n):
    return Cursor.UP(n)


def down(n):
    return Cursor.DOWN(n)


def forward(n):
    return Cursor.FORDWARD(n)


def back(n):
    return Cursor.BACK(n)


def outlog(mesaje):
    colors = [s for s in STYLE.findall(mesaje) if s in color]
    for s in colors:
        mesaje = mesaje.replace(s, color[s])
    print(mesaje + Style.RESET_ALL)


def rawlog(mesaje):
    colors = [s for s in STYLE.findall(mesaje) if s in color]
    for s in colors:
        mesaje = mesaje.replace(s, "")
    return mesaje
