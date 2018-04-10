#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import os
import time
from libs import config, control, utils, uriresolver
from libs.exceptions import Errornode
from multiprocessing import Process, Pipe, Queue
import threading
import traceback
import Pyro4
from termcolor import colored
from libs.inspection import _modules_libs_errors, show_warnings
import procname

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


class NODERB (control.Control):
    # revisar la carga posterior de parametros json
    def __init__(self, filename="", json=None):
        if json is None:
            json = {}
<<<<<<< HEAD
        super(NODERB,self).__init__()
=======
        super(NODERB, self).__init__()
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
        self.filename = filename  # Json file
        # Config from Json
        N_conf = config.Config(filename=filename, json=json)
        self.node = N_conf.node
        print(self.node)
        self.services = N_conf.services
        self.sensors = N_conf.sensors
        self.services_order = N_conf.services_order
        self.sensors_order = N_conf.sensors_order
        self.imports = N_conf.get_imports()
        self.PROCESS = {}
        import_class(*self.imports)
        exit()
        #iniciar el nodo principal
        #obtener conexion al URI_resolv del nodo
        #obtener la uri del nodo


        #arrancar servicios y sensores

        #enviar la informacion de procesos al nodo


        self.load_node(self, **self.node)
        self.URI = None  # URIProxy for internal uri resolver
        self.URI_resolv = None  # Just URI for URI_RESOLV
        self.URI_object = self.load_uri_resolver()  # Object resolver location
<<<<<<< HEAD
        t = self.init_workers(self.create_server_node)
        time.sleep(0.8)
        self.PROCESS[self.name][1]=t
        procname.setprocname(self.uri_node)
        print(colored("\t|","yellow"))
        print(colored("\t|","yellow"))
        print(colored("\t+-----> SERVICES", "yellow"))

        self.load_objects(self.services, self.services_order)
        print(colored("\t|","yellow"))
        print(colored("\t|","yellow"))
        print(colored("\t+-----> PLUGINS", "yellow"))
        self.load_objects(self.sensors, self.sensors_order)


=======
        t = threading.Thread(target=self.create_server_node, args=())
        t.setDaemon(True)
        t.start()
        time.sleep(0.8)
        self.PROCESS[self.name][1] = t
        print(colored("\t|", "yellow"))
        print(colored("\t|", "yellow"))
        print(colored("\t+-----> SERVICES", "yellow"))

        self.load_objects(self.services, self.N_conf.services_order)
        print(colored("\t|", "yellow"))
        print(colored("\t|", "yellow"))
        print(colored("\t+-----> PLUGINS", "yellow"))
        self.load_objects(self.sensors, self.N_conf.sensors_order)

    @control.load_node
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
    def load_node(self, data, **kwargs):
        global ROBOT_PASSWORD
        for k,v in kwargs.items():
            setattr(self,k,v)
        ROBOT_PASSWORD = self.name
        print("")
        print(colored("_________PYRO4BOT SYSTEM__________", "yellow"))
        print("\tEthernet device {} IP: {}".format(
            colored(self.ethernet, "cyan"), colored(self.ip, "cyan")))
        print("\tPassword: {}".format(colored(ROBOT_PASSWORD, "cyan")))
        print("\tFilename: {}".format(colored(self.filename, 'cyan')))
<<<<<<< HEAD

=======
        self.PROCESS = {}
        self.sensors = self.N_conf.sensors
        self.services = self.N_conf.services
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f

    def load_uri_resolver(self):
        uri_r = uriresolver.uriresolver(self.node,
                                        password=ROBOT_PASSWORD)
        self.URI_resolv, self.URI = uri_r.register_uriresolver()
        return uri_r

    def load_objects(self, parts, object_robot):
        for k in object_robot:
            parts[k]["_local_trys"] = _LOCAL_TRAYS
            parts[k]["_remote_trys"] = _REMOTE_TRAYS
            parts[k]["_services_trys"] = _LOCAL_TRAYS
            parts[k]["_unresolved_locals"] = list(parts[k].get("_locals", []))
<<<<<<< HEAD
            parts[k]["_unr_remote_deps"] = list(parts[k].get("_resolved_remote_deps", []))
            parts[k]["_unresolved_services"] = list(parts[k].get("_services", []))
=======
            parts[k]["_unr_remote_deps"] = list(
                parts[k].get("_resolved_remote_deps", []))
            parts[k]["_unresolved_services"] = list(
                parts[k].get("_services", []))
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
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
<<<<<<< HEAD
                print "[%s]  STARTING %s Error in locals %s" % (colored(st_local, 'red'), k, parts[k]["_unresolved_locals"])
                continue
            if st_remote == "ERROR":
                print "[%s]  STARTING %s Error in remotes %s" % (colored(st_remote, 'red'), k, parts[k]["_unr_remote_deps"])
=======
                print "[%s]  NOT STARTING %s Error in locals %s" % (colored(st_local, 'red'), k, parts[k]["_unresolved_locals"])
                continue

            if "ERROR" in st_remote:
                print "[{}] {} {} --> {}".format(
                    colored("ERROR", 'red'),
                    colored("NOT STARTING:", 'red'),
                    k,
                    colored("".join(parts[k]["_unr_remote_deps"]), 'red'))
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
                continue

            if st_service == "ERROR":
<<<<<<< HEAD
                print "[%s]  STARTING %s Error in service %s" % (colored(st_remote, 'red'), k, parts[k]["_unresolved_services"])
=======
                print "[%s]  NOT STARTING %s Error in service %s" % (colored(st_remote, 'red'), k, parts[k]["_unresolved_services"])
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
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
<<<<<<< HEAD
                parts[k].pop("-->",None)
=======
                parts[k].pop("-->", None)
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
                parts[k]["_REMOTE_STATUS"] = st_remote
                self.start_object(k, parts[k])

    def get_class_REQUIRED(self, cls):
        """ return a list of requeriments if cls has __REQUIRED class attribute"""
        try:
            dic_cls = eval("{0}.__dict__['_{0}__REQUIRED']".format(cls))
            return dic_cls
        except Exception:
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
<<<<<<< HEAD
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
=======
            if "WAIT" == msg:  # msg if working with generic ns
                obj["_remote_trys"] -= 1
                if obj["_remote_trys"] < 0:
                    check_remote = "ERROR"
                else:
                    check_remote = "WAIT"
                    time.sleep(1)
            elif "ERROR" == msg:  # msg if working with generic ns
                check_remote = (msg + ":" + d) if uri == d else uri
                obj["_remote_trys"] = 0
            elif "SYNC" == msg:   # msg if working with generic ns
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
                print("REMOTE-URI:{} , COMP:{}".format(uri, d))
                check_remote = "OK"
                obj["_remote_trys"] = 0
                obj["_resolved_remote_deps"].append(uri)
<<<<<<< HEAD
                if d in obj["_unr_remote_deps"]: obj["_unr_remote_deps"].remove(d)
            elif "ASYNC" == msg:
=======
                if d in obj["_unr_remote_deps"]:
                    obj["_unr_remote_deps"].remove(d)
            elif "ASYNC" == msg:  # msg if working with bigbrother ns
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
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
        attemps = 5
        if "_locals" not in obj:
            obj["_locals"] = []
        if "_resolved_remote_deps" not in obj:
            obj["_resolved_remote_deps"] = []
        if name not in self.PROCESS:
            self.PROCESS[name] = []
            obj["pyro4id"] = self.URI.new_uri(name, obj["mode"])
            obj["name"] = name
            obj["node"] = self.uri_node
            obj["uriresolver"] = self.URI_resolv
            procname.setprocname(obj["pyro4id"])
            self.PROCESS[name].append(obj["pyro4id"])
            self.PROCESS[name].append(
                Process(name=name, target=self.pyro4bot_object, args=(obj, client_pipe)))
            self.PROCESS[name][1].start()
            self.PROCESS[name].append(self.PROCESS[name][1].pid)
<<<<<<< HEAD

            # TODO: Async recv or timeout

=======
            self.PROCESS[name].append(obj["_REMOTE_STATUS"])
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            status = serv_pipe.recv()
            status = "FAIL"
            while (attemps > 0):
                try:
                    pxy = utils.get_pyro4proxy(obj["pyro4id"], self.name)
                    status = pxy.get_status()
                    break
                except Exception:
                    attemps -= 1
                    time.sleep(0.5)
            if status == "OK":
                st = colored(status, 'green')
                self.PROCESS[name].append(pxy.__docstring__())
            if status == "FAIL":
                st = colored(status, 'red')
            if status == "WAITING":
                st = colored(status, 'yellow')
<<<<<<< HEAD
            print "\t\t[%s]  STARTING %s" % (st, obj["pyro4id"])
=======
            if status == "ASYNC":
                print "\t\t[%s] STARTING %s --> remotes dependencies in asynchronous mode with --> %s" % (colored(status, 'yellow'), name, colored(' '.join(obj["_unr_remote_deps"]), 'yellow'))
            else:
                print "\t\t[%s] STARTING %s" % (st, obj["pyro4id"])
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
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
<<<<<<< HEAD
=======

            proc_pipe.send("CONTINUE")
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f

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
<<<<<<< HEAD
                safe_exposed[k] = list(set(exposed[k]) - set(dir(control.Control)))
=======
                safe_exposed[k] = list(
                    set(exposed[k]) - set(dir(control.Control)))
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            safe_exposed["methods"].extend(["__docstring__", "__exposed__"])
            new_object.exposed.update(safe_exposed)

            # Save dosctring documentation inside sensor object
            new_object.docstring.update(
                self.add_docstring(new_object, safe_exposed))

<<<<<<< HEAD
            if ("_REMOTE_STATUS") in deps and deps["_REMOTE_STATUS"] == "WAITING":
                proc_pipe.send("WAITING")
            else:
                proc_pipe.send("OK")
=======

>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            daemon.requestLoop()
            print("[%s] Shutting %s" %
                  (colored("Down", 'green'), d["pyro4id"]))
        except Exception as e:
            proc_pipe.send("FAIL")
            print("ERROR: creating sensor robot object: " + d["pyro4id"])
            print utils.format_exception(e)

    def create_server_node(self):
        try:
            # Daemon proxy for node robot
            self.port_node = utils.get_free_port(self.port_node)
            daemon = Pyro4.Daemon(host=self.ip, port=self.port_node)
            daemon._pyroHmacKey = bytes(ROBOT_PASSWORD)

            # Associate object (node) to the daemon
            self.uri_node = daemon.register(self, objectId=self.name)

            # Get exposed methods from node
            self.exposed = Pyro4.core.DaemonObject(
                daemon).get_metadata(self.name, True)
            # Get docstring from exposed methods on node
            self.docstring = self.add_docstring(self, self.exposed)

<<<<<<< HEAD


            # Registering NODE on nameserver
            self.URI.register_robot_on_nameserver(self.uri_node)
            self.PROCESS[self.name] = []
            self.uri_node=self.URI.new_uri(self.name)
=======
            # Registering NODE on nameserver
            self.URI.register_robot_on_nameserver(self.uri_node)
            self.PROCESS[self.name] = []
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            self.PROCESS[self.name].append(self.uri_node)
            self.PROCESS[self.name].append(None)
            self.PROCESS[self.name].append(os.getpid())
            self.PROCESS[self.name].append("OK")
            self.PROCESS[self.name].append(self.docstring)
            # Printing info
            print(colored(
<<<<<<< HEAD
                 "____________STARTING PYRO4BOT NODE %s_______________________" % self.name, "yellow"))
            print("[%s]  PYRO4BOT: %s" % (colored("OK", 'green'), self.uri_node))
            daemon.requestLoop()
            print("[%s] Final shutting %s" % (colored("Down", 'green'), self.uri_node))
=======
                "____________STARTING PYRO4BOT NODE %s_______________________" % self.name, "yellow"))
            print("[%s]  PYRO4BOT: %s" %
                  (colored("OK", 'green'), self.uri_node))
            daemon.requestLoop()
            print("[%s] Final shutting %s" %
                  (colored("Down", 'green'), self.uri_node))
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
            os._exit(0)
        except Exception:
            print("ERROR: create_server_node in node.py")
            raise

    def shutdown(self):
        print(colored("____STOPPING PYRO4BOT %s_________" % self.name, "yellow"))
        for k, v in self.PROCESS.items():
            try:
                if isinstance(v[1], threading.Thread):
                    pass
                else:
                    v[1].terminate()
            except:
                raise
            print("[{}]  {}".format(colored("Down", 'green'), v[0]))

    def print_process(self, onlyChanges=False):
        for k, v in self.PROCESS.iteritems():
            #  Update status
            try:
                old_status = v[3]
                v[3] = utils.get_pyro4proxy(v[0], self.name).get_status()
            except Exception:
                v[3] = "FAIL"

            if ((onlyChanges and v[3] != old_status) or not onlyChanges):
                if v[3] == "OK": st = colored(v[3], 'green')
                elif v[3] == "FAIL": st = colored(v[3], 'red')
                elif v[3] == "WAITING" or v[3] == "ASYNC": st = colored(v[3], 'yellow')
                print("[{}]\t{} {}".format(st, str(v[2]), str(v[0]).rjust(60, ".")))


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
    def get_uris(self):
        return self.URI.list_uris()

    @Pyro4.expose
    def get_name_uri(self, name):
        if name in self.PROCESS:
            uri = self.URI.get_uri(name)
            status = self.PROCESS[name][3]
            return uri, status
        else:
            return None, "down"

    def shutdown(self):
        print(colored("____STOPING PYRO4BOT %s_________" % self.name, "yellow"))
        for k,v in self.PROCESS.items():
            try:
                if isinstance(v[1],threading.Thread):
                    pass
                else:
                    v[1].terminate()
            except:
                raise
            print("[{}]  {}".format(colored("Down", 'green'), v[0]))

    @Pyro4.expose
<<<<<<< HEAD
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


class node(control.Control):
    def __init__(self,node):
        self.PROCESS = {}
        self.URI = None
        self.URI_resolv = None
        self.load_uri_resolver()  # Object resolver location

    def load_uri_resolver(self):
        """
        URI is a proxy for uri_resolver
        URI_resolv is str uri for resolver
        """
        self.URI_object = uriresolver.uriresolver(self.node,
                                        password=ROBOT_PASSWORD)
        # Just URI for URI_RESOLV
        self.URI_resolv, self.URI = uri_r.register_uriresolver()


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

    def shutdown(self):
        print(colored("____STOPING PYRO4BOT %s_________" % self.name, "yellow"))
        for k,v in self.PROCESS.items():
            try:
                if isinstance(v[1],threading.Thread):
                    pass
                else:
                    v[1].terminate()
            except:
                raise
            print("[{}]  {}".format(colored("Down", 'green'), v[0]))

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
=======
>>>>>>> c61fcabd7e40f8ec7e412a05440fd74f5c16fc3f
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring

    @Pyro4.expose
    def get_status(self):
        return "OK"

    # @Pyro4.expose
    # def change_comp_status(self, name, status):
    #     print self.PROCESS[name]

    @Pyro4.expose
    def status_changed(self):
        self.print_process(onlyChanges=True)
