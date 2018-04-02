#!/usr/bin/env python
"""PYRO4BOT Launcher.

Main file
"""
import node.node as nodo
import sys
import os

try:
    if len(sys.argv) > 1:
        jsonbot = sys.argv[1]
    else:
        jsonbot = "./samples/simplebot.json"
    nod = nodo.NODERB(filename=jsonbot)
except IOError:
    print("The file can not be found: %s" % jsonbot)
    raise
except (KeyboardInterrupt, SystemExit):
    os._exit(0)
