#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________

from _client_robot import ClientRobot
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot = ClientRobot(sys.argv[1])
    else:
        print("Error. Introducir nombre robot por parametro.")
