#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import os
import time
from libs import config, control, utils, uriresolver
from libs.exceptions import Errornode
from multiprocessing import Process, Pipe
import multiprocessing
import threading
import traceback
import Pyro4
from termcolor import colored
from libs.inspection import _modules_libs_errors, show_warnings

show_warnings(_modules_libs_errors)
BIGBROTHER_PASSWORD = "PyRobot"
ROBOT_PASSWORD = "default"
_LOCAL_TRAYS = 5
_REMOTE_TRAYS = 5


def import_class(services, sensors):
    """ Import necesary packages for robot"""
    print(colored("\n____________IMPORTING CLASS FOR ROBOT______________________",
                  'yellow'))
    print(" SERVICES:")
    for module, cls in services:
        try:
            print(colored("      FROM {} IMPORT {}".format(module, cls), "cyan"))
            exec("from {} import {}".format(module, cls), globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls, module))
            traceback.print_exc()
            exit(0)
    print(" SENSORS:")
    for module, cls in sensors:
        try:
            print(colored("      FROM {} IMPORT {}".format(module, cls), "cyan"))
            exec("from {} import {}".format(module, cls), globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls, module))
            traceback.print_exc()
            exit(0)

# ___________________CLASS NODERB________________________________________


class NODERB (object):
    # revisar la carga posterior de parametros json
    def __init__(self, filename="", json=None):
        if json is None:
            json = {}

        self.filename = filename  # Json file
        self.N_conf = config.Config(
            filename=filename, json=json)  # Config from Json
        self.load_node(self, PROCESS={}, **self.N_conf.node)
        import_class(*self.N_conf.get_imports())
        self.URI = None  # URIProxy for internal uri resolver
        self.URI_resolv = None  # Just URI for URI_RESOLV
        self.URI_object = self.load_uri_resolver()  # Object resolver location
        print(colored("\n_________STARTING PYRO4BOT SERVICES__________________", "yellow"))

        self.load_objects(self.services, self.N_conf.services_order)
        print(colored("\n_________STARTING PYRO4BOT COMPONENTS___________________", "yellow"))
        self.load_objects(self.sensors, self.N_conf.sensors_order)

        self.create_server_node()

    @control.load_node
    def load_node(self, data, **kwargs):
        global ROBOT_PASSWORD
        ROBOT_PASSWORD = self.name
        print(colored("\n_________STARTING PYRO4BOT SYSTEM__________", "yellow"))
        print("  Ethernet device {} IP: {}".format(
            colored(self.ethernet, "cyan"), colored(self.ip, "cyan")))
        print("  Password: {}".format(colored(ROBOT_PASSWORD, "cyan")))
        print("  Filename: {}".format(colored(self.filename, 'cyan')))
        self.PROCESS = {}
        self.sensors = self.N_conf.sensors
        self.services = self.N_conf.services

    def load_uri_resolver(self):
        uri_r = uriresolver.uriresolver(self.N_conf.node,
                                        password=ROBOT_PASSWORD)
        self.URI_resolv, self.URI = uri_r.register_uriresolver()
        return uri_r

    def load_objects(self, parts, object_robot):
        for k in object_robot:
            parts[k]["_local_trys"] = _LOCAL_TRAYS
            parts[k]["_remote_trys"] = _REMOTE_TRAYS
            parts[k]["_services_trys"] = _LOCAL_TRAYS
            parts[k]["_unresolved_locals"] = list(parts[k].get("_locals", []))
            parts[k]["_unr_remote_deps"] = list(parts[k].get("_resolved_remote_deps", []))
            parts[k]["_unresolved_services"] = list(parts[k].get("_services", []))
            parts[k]["_non_required"] = self.check_requireds(parts[k])
        errors = False
        for k in object_robot:
            if parts[k]["_non_required"]:
                print(colored("ERROR: class {} require {} for {}  ".
                              format(parts[k]["cls"], parts[k]["_non_required"], k), "red"))
                errors = True
        if errors:
            exit()
        while object_robot != []:
            k = object_robot.pop(0)
            st_local, st_remote, st_service = self.check_deps(k, parts[k])
            if st_local == "ERROR":
                print "[%s]  STARTING %s Error in locals %s" % (colored(st_local, 'red'), k, parts[k]["_unresolved_locals"])
                continue
            if st_remote == "ERROR":
                print "[%s]  STARTING %s Error in remotes %s" % (colored(st_remote, 'red'), k, parts[k]["_unr_remote_deps"])
                continue
            if st_service == "ERROR":
                print "[%s]  STARTING %s Error in service %s" % (colored(st_remote, 'red'), k, parts[k]["_unresolved_services"])
                continue

            if st_local == "WAIT" or st_remote == "WAIT" or st_service == "WAIT":
                object_robot.append(k)
                continue

            if st_local == "OK" and st_service == "OK":
                del(parts[k]["_unresolved_locals"])
                del(parts[k]["_local_trys"])
                del(parts[k]["_unresolved_services"])
                del(parts[k]["_services_trys"])
                del(parts[k]["_remote_trys"])
                parts[k].pop("-->",None)
                parts[k]["_REMOTE_STATUS"] = st_remote
                self.start_object(k, parts[k])

    def get_class_REQUIRED(self, cls):
        """ return a list of requeriments if cls has __REQUIRED class attribute"""
        try:
            dic_cls = eval("{0}.__dict__['_{0}__REQUIRED']".format(cls))
            return dic_cls
        except:
            return []

    def check_requireds(self, obj):
        """
        for a given obj this method calc requeriments class and
        get unfulfilled requeriments for an obj
        inside _service and _local find on left side string
        """
        requireds = self.get_class_REQUIRED(obj["cls"])
        connectors = obj.get("_services", []) + obj.get("_locals", [])
        keys = list(obj.keys()) + obj.get("_resolved_remote_deps", [])
        unfulfilled = [x for x in requireds if x not in
                       map(lambda x:x.split(".")[1], connectors) + keys]
        return unfulfilled

    def check_local_deps(self, obj):
        check_local = "OK"
        for d in obj["_unresolved_locals"]:
            uri = self.URI.wait_local_available(d, ROBOT_PASSWORD)
            if uri is not None:
                obj["_locals"].append(uri)
            else:
                obj["_local_trys"] -= 1
                if obj["_local_trys"] < 0:
                    check_local = "ERROR"
                    break
                else:
                    check_local = "WAIT"
                    break
        return check_local

    def check_service_deps(self, obj):
        check_service = "OK"
        for d in obj["_unresolved_services"]:
            uri = self.URI.wait_local_available(d, ROBOT_PASSWORD)
            if uri is not None:
                obj["_services"].append(uri)
            else:
                obj["_services_trys"] -= 1
                if obj["_services_trys"] < 0:
                    check_service = "ERROR"
                    break
                else:
                    check_service = "WAIT"
                    break
        return check_service

    def check_remotes(self, k, obj):
        check_remote = "OK"
        for d in obj["_unr_remote_deps"]:
            msg, uri = self.URI.wait_resolv_remotes(d, k)
            if "WAIT" == msg:
                obj["_remote_trys"] -= 1
                if obj["_remote_trys"] < 0:
                    check_remote = "WAITING"
                else:
                    check_remote = "WAIT"
                    time.sleep(1)
            elif "ERROR" == msg:
                check_remote = "ERROR"
                obj["_remote_trys"] = 0
            elif "SYNC" == msg:
                print("REMOTE-URI:{} , COMP:{}".format(uri, d))
                check_remote = "OK"
                obj["_remote_trys"] = 0
                obj["_resolved_remote_deps"].append(uri)
                if d in obj["_unr_remote_deps"]: obj["_unr_remote_deps"].remove(d)
            elif "ASYNC" == msg:
                check_remote = "ASYNC"
                obj["_remote_trys"] = 0
            else:
                check_remote = "UNKNOWN-ERROR"
                obj["_remote_trys"] = 0
        return check_remote

    def check_deps(self, k, obj):
        obj["_locals"] = []
        obj["_resolved_remote_deps"] = []
        obj["_services"] = []
        check_local = self.check_local_deps(obj)
        check_services = self.check_service_deps(obj)
        check_remote = self.check_remotes(k, obj)
        return check_local, check_remote, check_services

    def start_object(self, name, obj):
        serv_pipe, client_pipe = Pipe()
        if "_locals" not in obj:
            obj["_locals"] = []
        if "_resolved_remote_deps" not in obj:
            obj["_resolved_remote_deps"] = []
        if name not in self.PROCESS:
            self.PROCESS[name] = []
            obj["pyro4id"] = self.URI.new_uri(name, obj["mode"])
            obj["name"] = name
            obj["uriresolver"] = self.URI_resolv
            self.PROCESS[name].append(obj["pyro4id"])
            self.PROCESS[name].append(
                Process(name=name, target=self.pyro4bot_object, args=(obj, client_pipe)))
            self.PROCESS[name][1].start()
            self.PROCESS[name].append(self.PROCESS[name][1].pid)

            # TODO: Async recv or timeout

            status = serv_pipe.recv()
            self.PROCESS[name].append(status)
            if status == "OK":
                st = colored(status, 'green')
                self.PROCESS[name].append(utils.get_pyro4proxy(
                    obj["pyro4id"], self.name).__docstring__())
            if status == "FAIL":
                st = colored(status, 'red')
            if status == "WAITING":
                st = colored(status, 'yellow')
            print "[%s]  STARTING %s" % (st, obj["pyro4id"])
        else:
            print("ERROR: " + name + " is runing")

    def pyro4bot_object(self, d, proc_pipe):
        (name_ob, ip, ports) = utils.uri_split(d["pyro4id"])
        try:
            # Daemon proxy for sensor
            daemon = Pyro4.Daemon(
                host=ip, port=utils.get_free_port(ports, ip=ip))
            daemon._pyroHmacKey = bytes(ROBOT_PASSWORD)
            deps = utils.prepare_proxys(d, ROBOT_PASSWORD)

            # Preparing class for pyro4
            pyro4bot_class = control.Pyro4bot_Loader(globals()[d["cls"]], deps)
            new_object = pyro4bot_class()

            # Associate object to the daemon
            uri = daemon.register(new_object, objectId=name_ob)

            # Get and save exposed methods
            exposed = Pyro4.core.DaemonObject(
                daemon).get_metadata(name_ob, True)

            # Hide methods from Control
            safe_exposed = {}
            for k in exposed.keys():
                safe_exposed[k] = list(set(exposed[k]) - set(dir(control.Control)))
            safe_exposed["methods"].extend(["__docstring__", "__exposed__"])
            new_object.exposed.update(safe_exposed)

            # Save dosctring documentation inside sensor object
            new_object.docstring.update(
                self.add_docstring(new_object, safe_exposed))

            if ("_REMOTE_STATUS") in deps and deps["_REMOTE_STATUS"] == "WAITING":
                proc_pipe.send("WAITING")
            else:
                proc_pipe.send("OK")
            daemon.requestLoop()
            print("[%s] Shutting %s" %
                  (colored("Down", 'green'), d["pyro4id"]))
        except Exception as e:
            proc_pipe.send("FAIL")
            print("ERROR: creating sensor robot object: " + d["pyro4id"])
            print utils.format_exception(e)

    def create_server_node(self):
        uri = None
        try:
            # Daemon proxy for node robot
            self.port_node = utils.get_free_port(self.port_node)
            daemon = Pyro4.Daemon(host=self.ip, port=self.port_node)
            daemon._pyroHmacKey = bytes(ROBOT_PASSWORD)

            # Associate object (node) to the daemon
            uri = daemon.register(self, objectId=self.name)

            # Get exposed methods from node
            self.exposed = Pyro4.core.DaemonObject(
                daemon).get_metadata(self.name, True)
            # Get docstring from exposed methods on node
            self.docstring = self.add_docstring(self, self.exposed)

            # Registering NODE on nameserver
            self.URI.register_robot_on_nameserver(uri)

            # Printing info
            print(colored(
                "\n____________STARTING PYRO4BOT %s_______________________" % self.name, "yellow"))
            print("[%s]  PYRO4BOT: %s" % (colored("OK", 'green'), uri))
            self.print_process()
            daemon.requestLoop()
            print("[%s] Final shutting %s" % (colored("Down", 'green'), uri))
            os._exit(0)
        except Exception:
            print("ERROR: create_server_node in node.py")
            raise

    @Pyro4.expose
    def get_uris(self):
        return self.URI.list_uris()

    @Pyro4.expose
    def get_name_uri(self, name):
        # print self.URI.list_uris()
        if name in self.PROCESS:
            uri = self.URI.get_uri(name)
            status = self.PROCESS[name][3]
            return uri, status
        else:
            return None, "down"

    @Pyro4.expose
    def print_process(self):
        for k, v in self.PROCESS.iteritems():
            name = v[0]
            pid = str(v[2])
            status = str("[" + colored(v[3], 'green') + "]")
            print(status.ljust(17, " ") + pid + name.rjust(50, "."))
            # print(v[-1])

    def add_docstring(self, new_object, exposed):
        """Return doc_string documentation in methods_and_docstring"""
        docstring = {}
        for key in filter(lambda x: x in ["methods", "oneway"], exposed.keys()):
            for m in exposed[key]:
                if (m not in ["__docstring__", "__exposed__"]):  # Exclude docstring method
                    d = eval("new_object." + str(m) + ".__doc__")
                    docstring[m] = d
        return docstring

    @Pyro4.expose
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring
