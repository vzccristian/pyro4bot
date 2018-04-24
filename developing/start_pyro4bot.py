#!/usr/bin/env python
"""PYRO4BOT Launcher.

Main file
"""
import node.robotstarter as robot
import sys
import time
import os
from termcolor import colored
import setproctitle
import Pyro4
from node.libs import utils
try:
    if len(sys.argv) > 1:
        jsonbot = sys.argv[1]
    else:
        jsonbot = "./samples/simplebot.json"
    PROCESS = robot.robot_starter(filename=jsonbot)
    #print(PROCESS)
    setproctitle.setproctitle(PROCESS[0]+"."+"Console")
    ROB = utils.get_pyro4proxy(PROCESS[1],PROCESS[0])
    salir = True
    while salir:
        cad=raw_input("{}: ".format(PROCESS[0]))

        if cad.upper()=="EXIT":
            ROB.shutdown()
            os.kill(PROCESS[3],9)
            exit()
        if cad.upper() == "STATUS":
            ROB.print_process()
        if cad.upper() == "DOC":
            for k,v in ROB.__docstring__().items():
                print(k)
                print("\t"+str(v))
        if cad.upper() == "SALIR":
            salir = False
            exit()
except IOError:
    print("The file can not be found: %s" % jsonbot)
    raise
except (KeyboardInterrupt, SystemExit):
    # ROB.shutdown()
    os._exit(0)
