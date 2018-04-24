#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import os
import time
from libs import config, control, utils, uriresolver
from libs.exceptions import Errornode
from multiprocessing import Process, Pipe, Queue
import Pyro4
from termcolor import colored
from libs.inspection import _modules_libs_errors, show_warnings
import setproctitle
from node import *

BIGBROTHER_PASSWORD = "PyRobot"
ROBOT_PASSWORD = "default"


# ___________________ROBOT STARTER________________________________________
def create_server_node(robot,proc_pipe, msg):
    try:
        # Daemon proxy for node robot
        node = robot["node"]
        for k,v in node.items():
            robot[k]=v
        setproctitle.setproctitle(robot["name"]+"."+"ROBOT")
        robot["port_node"] = utils.get_free_port(robot["port_node"])
        daemon = Pyro4.Daemon(host=robot["ip"], port=robot["port_node"])
        daemon._pyroHmacKey = bytes(ROBOT_PASSWORD)
        pyro4bot_class = control.Pyro4bot_Loader(globals()["robot"], **robot)
        new_object = pyro4bot_class()

        # Associate object to the daemon
        uri_node = daemon.register(new_object, objectId=robot["name"])

        # Get and save exposed methods
        exposed = Pyro4.core.DaemonObject(
            daemon).get_metadata(robot["name"], True)

        # URI_resolv = new_object.URI_resolv
        #self.uri_node = new_object.pyro4id

        new_object.mypid = os.getpid()
        new_object.uri_node = uri_node
        #new_object.pyro4id = uri_node

        # Get exposed methods from node
        exposed = Pyro4.core.DaemonObject(
            daemon).get_metadata(node["name"], True)
        # Get docstring from exposed methods on node
        new_object.docstring = new_object.add_docstring(new_object,exposed)
        # Printing info
        print(colored(
            "____________STARTING PYRO4BOT NODE %s_______________________" % robot["name"], "yellow"))
        print("[%s]  PYRO4BOT: %s" %
              (colored("OK", 'green'), uri_node))

        new_object.start_plugins()
        msg.put((uri_node, os.getpid()))
        proc_pipe.send("CONTINUE")
        daemon.requestLoop()
        print("[%s] Final shutting %s" %
              (colored("Down", 'green'), uri_node))
        os._exit(0)
    except Exception:
        #print("ERROR: create_server_node in node.py")
        raise

def load_robot(robot):
    global ROBOT_PASSWORD
    serv_pipe, client_pipe = Pipe()
    msg = Queue()

    ROBOT_PASSWORD = robot["node"]["name"]
    print("")
    print(colored("_________PYRO4BOT SYSTEM__________", "yellow"))
    print("\tEthernet device {} IP: {}".format(
        colored(robot["node"]["ethernet"], "cyan"), colored(robot["node"]["ip"], "cyan")))
    print("\tPassword: {}".format(colored(ROBOT_PASSWORD, "cyan")))
    print("\tFilename: {}".format(colored(robot["filename"], 'cyan')))
    print("")
    name = robot["node"]["name"]
    PROCESS=[]
    PROCESS.append(name)
    PROCESS.append("pyro4id")
    proc = Process(name=name, target=create_server_node, args=(robot, client_pipe, msg,))
    proc.start()
    PROCESS.append(proc)
    status = serv_pipe.recv()

    uri_node, pid= msg.get()
    PROCESS[1] = uri_node
    PROCESS.append(pid)
    PROCESS.append("OK")
    return PROCESS

def robot_starter(filename="",json=None):
    if json is None: json = {}
    N_conf = config.Config(filename=filename, json=json)
    robot = N_conf.robot
    robot["filename"] = filename
    setproctitle.setproctitle(robot["node"]["name"]+"."+"Starter")
    PROCESS = load_robot(robot)
    return PROCESS
