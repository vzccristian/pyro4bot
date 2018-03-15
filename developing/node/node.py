#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import sys
import os
import time
import pprint
from libs import config, control, utils, uriresolver
from libs.exceptions import Errornode
from multiprocessing import Process, Pipe, Queue
import traceback
import Pyro4
import Pyro4.naming as nm
from termcolor import colored


BIGBROTHER_PASSWORD = "PyRobot"
ROBOT_PASSWORD = "default"
_LOCAL_TRAYS = 5
_REMOTE_TRAYS = 10

def import_class(services,sensors):
    """ Import necesary packages for robot"""
    print("")
    print(colored("____________IMPORTING CLASS FOR ROBOT______________________",
                      'yellow'))
    print(" SERVICES:")
    for module,cls in services:
        try:
            print(colored("      FROM {} IMPORT {}".format(module,cls), "cyan"))
            exec("from {} import {}".format(module,cls),globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls,module))
            traceback.print_exc()
            exit(0)
    print(" SENSORS:")
    for module,cls in sensors:
        try:
            print(colored("      FROM {} IMPORT {}".format(module,cls), "cyan"))
            exec("from {} import {}".format(module,cls),globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls,module))
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
        print("")
        print(colored("_________STARTING PYRO4BOT SERVICES__________________", "yellow"))
        self.load_objects(self.services,self.N_conf.services_order)
        print("")
        print(colored("_________STARTING PYRO4BOT PLUGINS___________________", "yellow"))
        self.load_objects(self.sensors,self.N_conf.sensors_order)

        self.create_server_node()

    @control.load_node
    def load_node(self, data, **kwargs):
        global ROBOT_PASSWORD
        ROBOT_PASSWORD = self.name
        print("")
        print(colored("_________STARTING PYRO4BOT SYSTEM__________","yellow"))
        print("  Ethernet device {} IP: {}".format(colored(self.ethernet,"cyan"),colored(self.ip,"cyan")))
        print("  Password: {}".format(colored(ROBOT_PASSWORD,"cyan")))
        print("  Filename: {}".format(colored(self.filename, 'cyan')))
        self.PROCESS = {}
        self.sensors = self.N_conf.sensors
        self.services = self.N_conf.services

    def load_uri_resolver(self):
        uri_r = uriresolver.uriresolver(self.N_conf.node,
                                        password=ROBOT_PASSWORD)
        self.URI_resolv, self.URI = uri_r.register_uriresolver()
        return uri_r

    def load_objects(self,parts,order):
        object_robot = order
        for k in object_robot:
            parts[k]["_local_trys"] = _LOCAL_TRAYS
            parts[k]["_remote_trys"] = _REMOTE_TRAYS
            parts[k]["_services_trys"] = _LOCAL_TRAYS
            parts[k]["nr_local"] = list(parts[k].get("_locals",[]))
            parts[k]["nr_remote"] = list(parts[k].get("_remotes",[]))
            parts[k]["nr_service"] = list(parts[k].get("_services",[]))
            parts[k]["_non_required"] = self.check_requireds(parts[k])
        errors=False
        for k in object_robot:
            if parts[k]["_non_required"]:
                print(colored("ERROR: class {} require {} for {}  ".
                              format(parts[k]["cls"],parts[k]["_non_required"],k),"red"))
                errors=True
        if errors:
            exit()

        while object_robot != []:
            k = object_robot.pop(0)
            st_local, st_remote, st_service = self.check_deps(parts[k])
            if st_local == "ERROR":
                print "[%s]  STARTING %s Error in locals %s" % (colored(st_local, 'red'), k, parts[k]["nr_local"])
                continue
            if st_remote == "ERROR":
                print "[%s]  STARTING %s Error in remotes %s" % (colored(st_remote, 'red'), k, parts[k]["nr_remote"])
                continue
            if st_service == "ERROR":
                print "[%s]  STARTING %s Error in service %s" % (colored(st_remote, 'red'), k, parts[k]["nr_service"])
                continue

            if st_local == "WAIT" or st_remote == "WAIT" or st_service == "WAIT":
                object_robot.append(k)
                continue

            if st_local == "OK" and st_service =="OK":
                del(parts[k]["nr_local"])
                del(parts[k]["_local_trys"])
                del(parts[k]["nr_service"])
                del(parts[k]["_services_trys"])
                if st_remote == "OK":
                    del(parts[k]["_remote_trys"])
                    del(parts[k]["nr_remote"])
                parts[k]["_REMOTE_STATUS"] = st_remote
                self.start__object(k, parts[k])

    def get_class_REQUIRED(self,cls):
        """ return a list of requeriments if cls has __REQUIRED class attribute"""
        try:
            dic_cls = eval("{0}.__dict__['_{0}__REQUIRED']".format(cls))
            return dic_cls
        except:
            return []

    def check_requireds(self,obj):
        """
        for a given obj this method calc requeriments class and
        get unfulfilled requeriments for an obj
        inside _service and _local find on left side string
        """
        requireds=self.get_class_REQUIRED(obj["cls"])
        connectors = obj.get("_services",[])+obj.get("_locals",[])
        keys = list(obj.keys())+obj.get("_remotes",[])
        unfulfilled = [x for x in requireds if x not in
                       map(lambda x:x.split(".")[1],connectors) + keys]
        return unfulfilled

    def check_local_deps(self, obj):
        check_local = "OK"
        for d in obj["nr_local"]:
            uri = self.URI.wait_available(d, ROBOT_PASSWORD)
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
        for d in obj["nr_service"]:
            uri = self.URI.wait_available(d, ROBOT_PASSWORD)
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

    def check_remote_deps(self, obj):
        check_remote = "OK"
        for d in obj["nr_remote"]:
            uri = self.URI.wait_resolv_remotes(d)
            if uri is None:
                check_remote = "ERROR"
                break
            print("REMOTE-URI:{} , COMP:{}".format(uri, d))
            if uri == d:
                obj["_remote_trys"] -= 1
                if obj["_remote_trys"] < 0:
                    check_remote = "WAITING"
                    break
                else:
                    check_remote = "WAIT"
                    break
            else:
                obj["_remotes"].append(uri)
        return check_remote

    def check_deps(self,obj):
        obj["_locals"] = []
        obj["_remotes"] = []
        obj["_services"] = []
        check_local = self.check_local_deps(obj)
        check_services = self.check_service_deps(obj)
        check_remote = self.check_remote_deps(obj)
        return check_local, check_remote, check_services

    def start__object(self, name, obj):
        serv_pipe, client_pipe = Pipe()
        if "_locals" not in obj:
            obj["_locals"] = []
        if "_remotes" not in obj:
            obj["_remotes"] = []
        if name not in self.PROCESS:
            self.PROCESS[name] = []
            obj["pyro4id"] = self.URI.new_uri(name, obj["mode"])
            obj["name"] = name
            obj["uriresolver"] = self.URI_resolv

            self.PROCESS[name].append(obj["pyro4id"])
            self.PROCESS[name].append(
                Process(name=name, target=self.pyro4bot__object, args=(obj, client_pipe)))
            self.PROCESS[name][1].start()
            self.PROCESS[name].append(self.PROCESS[name][1].pid)
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

    def pyro4bot__object(self, d, proc_pipe):
        (name_ob, ip, ports) = utils.uri_split(d["pyro4id"])
        try:
            # Daemon proxy for sensor
            daemon = Pyro4.Daemon(
                host=ip, port=utils.get_free_port(ports, ip=ip))
            daemon._pyroHmacKey = bytes(ROBOT_PASSWORD)

            # Sensor object
            new_object = eval(d["cls"])(data=[], **d)

            # Associate object to the daemon
            uri = daemon.register(new_object, objectId=name_ob)

            # Get and save exposed methods
            exposed = Pyro4.core.DaemonObject(
                daemon).get_metadata(name_ob, True)
            new_object.exposed.update(exposed)

            # Save dosctring documentation inside sensor object
            new_object.docstring.update(
                self.add_docstring(new_object, exposed))

            # print name_ob
            # print exposed
            # print new_object.docstring

            if d.has_key("_REMOTE_STATUS") and d["_REMOTE_STATUS"] == "WAITING":
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

            # print(self.exposed)
            # print(self.docstring)

            # Registering NODE on nameserver
            self.URI.register_robot_on_nameserver(uri)

            # Printing info
            print("")
            print(colored(
                "____________STARTING PYRO4BOT %s_______________________" % self.name, "yellow"))
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

    @Pyro4.expose
    def add_docstring(self, new_object, exposed):
        """Return doc_string documentation in methods_and_docstring"""
        docstring = {}
        for key in filter(lambda x: x in ["methods", "oneway"], exposed.keys()):
            for m in exposed[key]:
                if (m not in ["__docstring__", "__exposed__"]):  # Exclude docstring method
                    docstring[m] = eval("new_object." + str(m) + ".__doc__")
        return docstring

    @Pyro4.expose
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring
