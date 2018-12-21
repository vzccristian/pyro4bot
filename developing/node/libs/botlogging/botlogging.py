#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________
from .coloramadefs import *
import logging

class Logging(logging.Logger):
    def __init__(self):
        pass

    def message(self,men):
        outlog(men)

    def log(self,men):
        outlog(men)

    def posmsg(self,x,y,men):
        outlog(pos(x,y)+str(men))
