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
        jsonbot = "./samples/simplebot"
    nod = nodo.NODERB(filename=jsonbot)
except (KeyboardInterrupt, SystemExit):
    os._exit(0)
