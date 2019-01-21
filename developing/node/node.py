#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________

import os
import time
from node.libs import config, control, utils, uriresolver
from multiprocessing import Process, Pipe, Queue
import threading
import traceback
import Pyro4
from termcolor import colored
import setproctitle
from node.libs.inspection import _modules_libs_errors, show_warnings
import pprint

show_warnings(_modules_libs_errors)
_LOCAL_TRYS = 5
_REMOTE_TRYS = 5


def import_class(services, components):
    """ Import necessary packages for Robot"""
    print(colored("\n____________IMPORTING CLASS FOR ROBOT______________________",
                  'yellow'))
    print(" SERVICES:")
    for module, cls in services:
        try:
            print(colored("      FROM {} IMPORT {}".format(module, cls), "cyan"))
            # TODO : change that "node.{}" to the actual reference.
            exec("from node.{} import {}".format(module, cls), globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls, module))
            traceback.print_exc()
            exit(0)
    print(" COMPONENTS:")
    for module, cls in components:
        try:
            print(colored("      FROM {} IMPORT {}".format(module, cls), "cyan"))
            # TODO : change that "node.{}" to the actual reference.
            exec("from node.{} import {}".format(module, cls), globals())
        except Exception:
            print("ERROR IMPORTING CLASS: {} FROM MODULE {}".format(cls, module))
            traceback.print_exc()
            exit(0)
    print("")


class Robot(control.Control):
    """Main class Manage the robot."""

    def __init__(self):
        super(Robot, self).__init__()

        # Dictionary of components
        self.PROCESS = {}

        # Import objects needed to instantiate components
        import_class(*self.imports)

        # Resolution of URIs for Pyro
        self.URI_proxy = None  # URIProxy for internal uri resolver
        self.URI_uri = None  # Just URI for
        self.URI_object = self.load_uri_resolver()  # Object resolver location

    def load_uri_resolver(self):
        """Load the URIs resolver on main node."""
        uri_r = uriresolver.uriresolver(self.node,
                                        password=self.node["password"])
        self.URI_uri, self.URI_proxy = uri_r.register_uriresolver()
        return uri_r

    def start_components(self):
        """Launcher of node components."""
        # Decoration
        print((colored("\t|", "yellow")))
        print((colored("\t|", "yellow")))
        print((colored("\t+-----> SERVICES", "yellow")))
        self.load_objects(self.services, self.services_order)

        # Decoration
        print((colored("\t|", "yellow")))
        print((colored("\t|", "yellow")))
        print((colored("\t+-----> COMPONENTS", "yellow")))
        self.load_objects(self.components, self.components_order)

    def load_objects(self, parts, object_robot):
        """Execute the components or services of the node."""

        for k in object_robot:
            parts[k]["_local_trys"] = _LOCAL_TRYS
            parts[k]["_remote_trys"] = _REMOTE_TRYS
            parts[k]["_services_trys"] = _LOCAL_TRYS
            parts[k]["_unresolved_locals"] = list(parts[k].get("_locals", []))
            parts[k]["_unr_remote_deps"] = list(
                parts[k].get("_resolved_remote_deps", []))
            parts[k]["_unresolved_services"] = list(
                parts[k].get("_services", []))
            parts[k]["_non_required"] = self.check_requireds(parts[k])

        errors = False

        for k in object_robot:
            if parts[k]["_non_required"]:
                print((colored("ERROR: class {} require {} for {}  ".
                               format(parts[k]["cls"], parts[k]["_non_required"], k), "red")))
                errors = True

        if errors:
            exit()

        while object_robot != []:
            k = object_robot.pop(0)
            st_local, st_remote, st_service = self.check_deps(k, parts[k])

            if st_local == "ERROR":
                print("\t\t[%s]  NOT STARTING %s Error in locals %s" % (
                    colored(st_local, 'red'), k, parts[k]["_unresolved_locals"]))
                continue

            if "ERROR" in st_remote:
                print("\t\t[{}] {} {} --> {}".format(
                    colored("ERROR", 'red'),
                    colored("NOT STARTING:", 'red'),
                    k,
                    colored("".join(parts[k]["_unr_remote_deps"]), 'red')))
                continue

            if st_service == "ERROR":
                print("\t\t[%s]  NOT STARTING %s Error in service %s" % (
                    colored(st_remote, 'red'), k, parts[k]["_unresolved_services"]))
                continue
            if st_local == "WAIT" or st_remote == "WAIT" or st_service == "WAIT":
                object_robot.append(k)
                continue

            if st_local == "OK" and st_service == "OK":
                parts[k].pop("-->", None)
                parts[k]["_REMOTE_STATUS"] = st_remote
                del(parts[k]["_unresolved_locals"])
                del(parts[k]["_local_trys"])
                del(parts[k]["_unresolved_services"])
                del(parts[k]["_services_trys"])
                del(parts[k]["_remote_trys"])
                self.pre_start_pyro4bot_object(k, parts[k])

    def check_deps(self, k, obj):
        """Check the dependencies of the robot."""
        obj["_locals"] = []
        obj["_resolved_remote_deps"] = []
        obj["_services"] = []
        check_local = self.check_local_deps(obj)
        check_services = self.check_service_deps(obj)
        check_remote = self.check_remotes(k, obj)
        return check_local, check_remote, check_services

    def check_local_deps(self, obj):
        """Check the local dependencies of the robot."""
        check_local = "OK"
        for d in obj["_unresolved_locals"]:
            uri = self.URI_proxy.wait_local_available(d, self.node["password"])
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
        """Check the services dependencies of the robot."""
        check_service = "OK"
        for d in obj["_unresolved_services"]:
            uri = self.URI_proxy.wait_local_available(d, self.node["password"])
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
        """Check the remotes dependencies of the robot."""
        check_remote = "OK"
        for d in obj["_unr_remote_deps"]:
            msg, uri = self.URI_proxy.wait_resolv_remotes(d, k)
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
                print(("\t\t" + colored("*REMOTE-URI", 'green') + ":{} for comp:{}".format(uri, d)))
                check_remote = "OK"
                obj["_remote_trys"] = 0
                obj["_resolved_remote_deps"].append(uri)
                if d in obj["_unr_remote_deps"]:
                    obj["_unr_remote_deps"].remove(d)
            elif "ASYNC" == msg:
                check_remote = "ASYNC"
                obj["_remote_trys"] = 0
            else:
                check_remote = "UNKNOWN-ERROR"
                obj["_remote_trys"] = 0
        return check_remote

    def pre_start_pyro4bot_object(self, name, obj):
        """Pre starter for component."""
        serv_pipe, client_pipe = Pipe()
        attemps = 5
        if "_locals" not in obj:
            obj["_locals"] = []
        if "_resolved_remote_deps" not in obj:
            obj["_resolved_remote_deps"] = []
        if name not in self.PROCESS:
            self.PROCESS[name] = []
            obj["pyro4id"] = self.URI_proxy.new_uri(name, obj["mode"])
            obj["name"] = name
            obj["node"] = self.uri_node
            obj["uriresolver"] = self.URI_uri
            self.PROCESS[name].append(obj["pyro4id"])
            self.PROCESS[name].append(
                Process(name=name, target=self.start_pyro4bot_object, args=(obj, client_pipe)))
            self.PROCESS[name][1].start()
            self.PROCESS[name].append(self.PROCESS[name][1].pid)
            self.PROCESS[name].append(obj["_REMOTE_STATUS"])
            status = serv_pipe.recv()
            status = "FAIL"
            while (attemps > 0):
                try:
                    pxy = utils.get_pyro4proxy(
                        obj["pyro4id"], self.node["name"])
                    status = pxy.get_status()
                    break
                except Exception:
                    attemps -= 1
                    time.sleep(1)
            if status == "OK":
                st = colored(status, 'green')
                self.PROCESS[name].append(pxy.__docstring__())
            if status == "FAIL":
                st = colored(status, 'red')
            if status == "WAITING":
                st = colored(status, 'yellow')
            if status == "ASYNC":
                print("\t\t[%s] STARTING %s --> remotes dependencies in asynchronous mode with --> %s" % (
                    colored(status, 'yellow'), name, colored(' '.join(obj["_unr_remote_deps"]), 'yellow')))
            else:
                print("\t\t[%s] STARTING %s" % (st, obj["pyro4id"]))
        else:
            print(("ERROR: " + name + " is running"))

    def start_pyro4bot_object(self, d, proc_pipe):
        """Start PYRO4BOT component."""
        (name_ob, ip, ports) = utils.uri_split(d["pyro4id"])
        try:
            # Daemon proxy for sensor
            daemon = Pyro4.Daemon(
                host=ip, port=utils.get_free_port(ports, ip=ip))
            daemon._pyroHmacKey = bytes(self.node["password"], 'utf8')

            proc_pipe.send("CONTINUE")
            deps = utils.prepare_proxys(d, self.node["password"])

            # Preparing class for pyro4
            pyro4bot_class = control.Pyro4bot_Loader(
                globals()[d["cls"]], **deps)
            new_object = pyro4bot_class()

            # Associate object to the daemon
            uri = daemon.register(new_object, objectId=name_ob)

            # Get and save exposed methods
            exposed = Pyro4.core.DaemonObject(
                daemon).get_metadata(name_ob, True)

            # Hide methods from Control
            safe_exposed = {}
            for k in list(exposed.keys()):
                safe_exposed[k] = list(
                    set(exposed[k]) - set(dir(control.Control)))
            safe_exposed["methods"].extend(["__docstring__", "__exposed__"])
            new_object.exposed.update(safe_exposed)

            setproctitle.setproctitle("PYRO4BOT." + name_ob)
            # Save dosctring documentation inside sensor object
            new_object.docstring.update(
                self.get_docstring(new_object, safe_exposed))

            daemon.requestLoop()
            print(("[%s] Shutting %s" %
                   (colored("Down", 'green'), d["pyro4id"])))
        except Exception as e:
            proc_pipe.send("FAIL")
            print(("ERROR: creating sensor robot object: " + d["pyro4id"]))
            print(utils.format_exception(e))

    def get_docstring(self, new_object, exposed):
        """Return doc_string documentation in methods_and_docstring."""
        docstring = {}
        for key in [x for x in list(exposed.keys()) if x in ["methods", "oneway"]]:
            for m in exposed[key]:
                if (m not in (dir(control.Control))):  # Exclude control methods
                    d = eval("new_object." + str(m) + ".__doc__")
                    docstring[m] = d
        return docstring

    def get_class_REQUIRED(self, cls):
        """Return a list of requirements if cls has __REQUIRED class attribute."""
        try:
            dic_cls = eval("{0}.__dict__['_{0}__REQUIRED']".format(cls))
            return dic_cls
        except Exception:
            return []

    def check_requireds(self, obj):
        """
        For a given obj this method calc requirements class and
        get unfulfilled requirements for an obj
        inside _service and _local find on left side string.
        """
        requireds = self.get_class_REQUIRED(obj["cls"])
        connectors = obj.get("_services", []) + obj.get("_locals", [])
        keys = list(obj.keys()) + obj.get("_resolved_remote_deps", [])

        connectors = [self.node["name"] + '.' + con for con in connectors]

        unfulfilled = [req for req in requireds if req not in
                       [con.split(".")[1] for con in connectors] + keys]
        return unfulfilled

    def register_node(self):
        """Register main node on nameserver."""
        self.URI_proxy.register_robot_on_nameserver(self.uri_node)

    # Exposed methods (Publics)
    @Pyro4.expose
    def get_uris(self):
        """Return the URI of all the components of the robot."""
        return self.URI_proxy.list_uris()

    @Pyro4.expose
    def get_name_uri(self, name):
        """Return the URI of the given name as a component.

        @name: string.
                Follow the following format: "robotname.component"

        """
        if name in self.PROCESS:
            uri = self.URI_proxy.get_uri(name)
            status = self.PROCESS[name][3]
            return uri, status
        else:
            return None, "Not found"

    @Pyro4.expose
    def shutdown(self):
        print((colored("____STOPPING PYRO4BOT %s_________" %
                       self.node["name"], "yellow")))
        for k, v in list(self.PROCESS.items()):
            try:
                v[1].terminate()
            except Exception:
                raise
            print(("[{}]  {}".format(colored("Down", 'green'), v[0])))

    @Pyro4.expose
    def print_process(self, onlyChanges=False):
        for k, v in self.PROCESS.items():
            #  Update status
            try:
                old_status = v[3]
                v[3] = utils.get_pyro4proxy(
                    v[0], self.node["name"]).get_status()
            except Exception:
                v[3] = "FAIL"
            if (onlyChanges and v[3] != old_status) or not onlyChanges:
                if v[3] == "OK":
                    st = colored(v[3], 'green')
                elif v[3] == "FAIL":
                    st = colored(v[3], 'red')
                elif v[3] == "WAITING" or v[3] == "ASYNC":
                    st = colored(v[3], 'yellow')
                print(("[{}]\t{} {}".format(
                    st, str(v[2]), str(v[0]).rjust(60, "."))))

    @Pyro4.expose
    def status_changed(self):
        self.print_process(onlyChanges=True)
