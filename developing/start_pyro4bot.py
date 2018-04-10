#!/usr/bin/env python
"""PYRO4BOT Launcher.

Main file
"""
import node.node as nodo
import threading
import sys
import time
import os
from termcolor import colored


def init_thread(fn, *args):
    """ start  daemon"""
    t = threading.Thread(target=fn, args=args)
    t.setDaemon(True)
    t.start()
    return t


def init_thread( fn,*args):
    """ start  daemon"""
    t = threading.Thread(target=fn, args=args)
    t.setDaemon(True)
    t.start()
    return t

try:
    if len(sys.argv) > 1:
        jsonbot = sys.argv[1]
    else:
        jsonbot = "./samples/simplebot.json"
    NOD = nodo.NODERB(filename=jsonbot)
<<<<<<< HEAD
    #init_thread(NOD.create_server_node)
    time.sleep(0.5)
    salir = True
    while salir:
        cad=raw_input("{}: ".format(NOD.name))

        if cad.upper()=="EXIT":
=======
    # init_thread(NOD.create_server_node)
    time.sleep(0.5)
    while True:
        cad = raw_input("\n{}: ".format(colored(NOD.name,"green")))

        if cad.upper() == "EXIT":
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            NOD.shutdown()
            exit()
        if cad.upper() == "STATUS":
            NOD.print_process()
        if cad.upper() == "DOC":
<<<<<<< HEAD
            for k,v in NOD.__docstring__().items():
                print(k)
                print("\t"+str(v))
        if cad.upper() == "SALIR":
            salir = False
            exit()
=======
            for k, v in NOD.__docstring__().items():
                print(k)
                print("\t" + str(v))
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
except IOError:
    print("The file can not be found: %s" % jsonbot)
    raise
except (KeyboardInterrupt, SystemExit):
    os._exit(0)
