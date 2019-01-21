#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import Pyro4
from termcolor import colored
from multiprocessing import Process, Pipe
import setproctitle
from .node import Robot
import os
from queue import Queue
from node.libs import utils, control, config
# from .node import *


def start_node(robot, proc_pipe, msg):
    """Start node."""
    try:
        # Set process name
        setproctitle.setproctitle(
            "PYRO4BOT." + robot["node"]["name"] + "." + "ROBOT")

        # Daemon proxy for node robot
        robot["node"]["port_node"] = utils.get_free_port(
            robot["node"]["port_node"])

        daemon = Pyro4.Daemon(
            host=robot["node"]["ip"], port=robot["node"]["port_node"])
        daemon._pyroHmacKey = bytes(robot["node"]["password"], "utf8")

        pyro4bot_class = control.Pyro4bot_Loader(globals()["Robot"], **robot)
        new_object = pyro4bot_class()

        # Associate object to the daemon
        uri_node = daemon.register(new_object, objectId=robot["node"]["name"])

        # Get and save exposed methods
        exposed = Pyro4.core.DaemonObject(
            daemon).get_metadata(robot["node"]["name"], True)

        # Hide methods from Control
        safe_exposed = {}
        for k in list(exposed.keys()):
            safe_exposed[k] = list(
                set(exposed[k]) - set(dir(control.Control)))
        safe_exposed["methods"].extend(["__docstring__", "__exposed__"])

        new_object.exposed = safe_exposed

        new_object.mypid = os.getpid()
        new_object.uri_node = uri_node

        # Get docstring from exposed methods on node
        new_object.docstring = new_object.get_docstring(new_object, exposed)

        # Printing info
        print((colored(
            "____________STARTING PYRO4BOT NODE %s_______________________" % robot["node"]["name"], "yellow")))
        print(("[%s]  PYRO4BOT: %s" %
              (colored("OK", 'green'), uri_node)))

        new_object.start_components()

        print("after start components")

        msg.put((uri_node, os.getpid()))

        print("after msg.put")

        proc_pipe.send("OK")

        print("we're here")

        new_object.register_node()

        print("in the middle")

        print("hellooo:    ", robot["node"]["name"])

        print(daemon, '\t', type(daemon), '\t', daemon.locationStr)
        print("hi")
        print(daemon.locationStr)
        print(daemon.housekeeper_lock)
        print(daemon.natLocationStr)
        print(daemon.objectsById)
        print(daemon.streaming_responses)
        print(daemon.transportServer)
        print(daemon._pyroHmacKey)
        print(daemon._pyroHmacKey.decode())

        daemon.requestLoop()

        print("daemon request loop")

        print(("[%s] Final shutting %s" %
              (colored("Down", 'green'), uri_node)))
        os._exit(0)
    except Exception:
        print("ERROR: start_node in robotstarter.py")
        proc_pipe.send("ERROR")
        raise


def pre_start_node(robot):
    """Prerequisites to start robot."""
    # Pipe to wait for node to be ready
    serv_pipe, client_pipe = Pipe()
    msg = Queue()

    name = robot["node"]["name"]

    # Information
    print((colored("\n_________PYRO4BOT SYSTEM__________", "yellow")))
    print(("\tEthernet device {} IP: {}".format(
        colored(robot["node"]["ethernet"], "cyan"), colored(robot["node"]["ip"], "cyan"))))
    print(("\tRobot name: {}".format(colored(name, "cyan"))))
    print(("\tPassword: {}".format(colored(robot["node"]["password"], "cyan"))))
    print(("\tFilename: {}".format(colored(robot["filename"], 'cyan'))))
    print("")

    # Process for console
    PROCESS = []
    PROCESS.append(name)
    PROCESS.append("pyro4id")
    proc = Process(name=name, target=start_node,
                   args=(robot, client_pipe, msg,))
    proc.start()

    PROCESS.append(proc)
    status = serv_pipe.recv()  # Bloq until node ready
    uri_node, pid = msg.get()
    PROCESS[1] = uri_node
    PROCESS.append(pid)
    PROCESS.append(status)
    return PROCESS


def starter(filename="", json=None):
    """Get configuration and launch pre_starter."""
    if json is None:
        json = {}

    # Read JSON
    N_conf = config.Config(filename=filename, json=json)

    # Object for robot load
    robot = N_conf.robot
    robot["filename"] = filename

    # Set process name
    setproctitle.setproctitle(
        "PYRO4BOT." + robot["node"]["name"] + "." + "Starter")

    PROCESS = pre_start_node(robot)
    return PROCESS
