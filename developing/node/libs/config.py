#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________

import os.path
from node.libs import utils, myjson
from node.libs.inspection import _modules, _modules_errors, _classes, import_module
from termcolor import colored
import pprint


def get_field(search_dict, field, enable=True):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []
    for key, value in search_dict.items():
        if key == field:
            if isinstance(value, list):
                fields_found = fields_found + value
            else:
                fields_found.append(value)
        elif isinstance(value, dict):
            results = get_field(value, field)
            for result in results:
                fields_found.append(result)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_field(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)
    return fields_found


class Config:
    def __init__(self, filename="", json=None):
        self.conf = json if (filename == "") else myjson.MyJson(
            filename, dependencies=True).json

        self.set_lower_case()
        self.disable_lines()
        self.fix_config()

        self.services_order = self.dependency(self.services)
        self.components_order = self.dependency(self.components)

    def set_lower_case(self):
        self.conf = {k.lower(): self.conf[k] for k in list(self.conf.keys())}
        self.conf["node"] = {k.lower(): self.conf["node"][k] for k in
                             list(self.conf["node"].keys())}

    def disable_lines(self):
        for key in [x for x in list(self.conf.keys()) if x != "node"]:
            for k, v in list(self.conf[key].items()):
                if get_field(v, "enable") == [False]:
                    del(self.conf[key][k])

    def fix_config(self):
        # Add default frec
        if "def_frec" not in self.conf["node"]:
            self.conf["node"]["def_frec"] = 0.05

        # Add ethernet network
        if "ethernet" not in self.conf["node"]:
            self.conf["node"]["ethernet"] = utils.get_interface()

        # Add IP address
        if "ip" not in self.conf["node"]:
            self.conf["node"]["ip"] = utils.get_ip_address(
                self.conf["node"]["ethernet"])

        # Add default name
        if "name" not in self.conf["node"]:
            self.conf["node"]["name"] = "default_name"

        # Add port_ns
        if "port_ns" not in self.conf["node"]:
            self.conf["node"]["port_ns"] = 9090

        # Add port_node
        if "port_node" not in self.conf["node"]:
            self.conf["node"]["port_node"] = 4040

        # Add start_port
        if "start_port" not in self.conf["node"]:
            self.conf["node"]["start_port"] = 5050

        # Add def_worker
        if "def_worker" not in self.conf["node"]:
            self.conf["node"]["def_worker"] = True

        # Add password
        if "password" not in self.conf["node"]:
            self.conf["node"]["password"] = self.conf["node"]["name"]

        # Add bigbrother password
        if "bigbrother-password" not in self.conf["node"]:
            self.conf["node"]["bigbrother-password"] = "PyRobot"

        # Services and components config
        for k, v in list(self.components.items()) + list(self.services.items()):
            if "worker_run" not in v:
                v["worker_run"] = True
            if "mode" not in v:
                v["mode"] = "public"
            if "frec" not in v:
                v["frec"] = self.conf["node"]["def_frec"]
            v["docstring"] = {}
            v["exposed"] = {}
        for k, v in list(self.services.items()):
            v["mode"] = "local"

        # Services configuration
        newservices = {}
        for n in self.services:
            if _classes.get(self.services[n]["cls"], None) is not None:
                if len(_classes[self.services[n]["cls"]]) > 1:
                    print(("Warning: there are many modules {} for class {}".format(
                        _classes[self.services[n]["cls"]], self.services[n]["cls"])))
                self.services[n]["module"] = _classes[self.services[n]["cls"]][0]
                if "." not in n:
                    newservices[self.node["name"] + "." + n] = self.services[n]
                else:
                    newservices[n] = self.services[n]
            else:
                print((colored("ERROR: Class {} not found or error in Modules".format(
                    self.services[n]["cls"]), "red")))
                for k_error, error in _modules_errors.items():
                    print(("Module {}: {}".format(k_error, error)))
                exit()
            if ("-->") in self.services[n]:
                sp = [self.node["name"] + "." +
                      x for x in self.services[n]["-->"] if x.find(".") < 0]
                cp = [x for x in self.services[n]["-->"] if x.find(".") >= 0]
                self.services[n]["-->"] = sp + cp  # esto se puede simplificar

        self.services = newservices

        for n in self.services:
                    self.services[n]["_locals"] = []
                    self.services[n]["_resolved_remote_deps"] = []
                    if "-->" in self.services[n]:
                        self.services[n]["_locals"], self.services[n]["_resolved_remote_deps"] = self.local_remote(
                            self.services, n)
        newrobot = {}
        # Components configuration
        for n in self.components:
            if _classes.get(self.components[n]["cls"], None) is not None:
                if len(_classes[self.components[n]["cls"]]) > 1:
                    print(("Warning: there are many modules {} for class {}".format(
                        _classes[self.components[n]["cls"]], self.components[n]["cls"])))
                self.components[n]["module"] = _classes[self.components[n]["cls"]][0]
            else:
                print((colored("ERROR: Class {} not found or error in Modules".format(
                    self.components[n]["cls"]), "red")))
                for k_error, error in _modules_errors.items():
                    print(("Module {}: {}".format(k_error, error)))
                exit()
            self.components[n]["_services"] = list(self.services)
            if ("-->") in self.components[n]:
                sp = [self.node["name"] + "." +
                      x for x in self.components[n]["-->"] if x.find(".") < 0]
                cp = [x for x in self.components[n]["-->"] if x.find(".") >= 0]
                self.components[n]["-->"] = sp + cp  # esto se puede simplificar
            if n.find(".") == -1:
                newrobot[self.node["name"] + "." + n] = self.components[n]
            else:
                newrobot[n] = self.components[n]

        self.components = newrobot

        for n in self.components:
            self.components[n]["_locals"] = []
            self.components[n]["_unr_remote_deps"] = []
            self.components[n]["_resolved_remote_deps"] = []
            if "-->" in self.components[n]:
                self.components[n]["_locals"], self.components[n]["_resolved_remote_deps"] = self.local_remote(
                    self.components, n)

    def dependency(self, ser):
        ser_order = [x for x in ser if not get_field(ser[x], "_locals")]
        condep = [x for x in ser if get_field(ser[x], "_locals")]
        nivel_dep = 0
        while condep and nivel_dep < 20:
            for i in condep:
                dep_nec = [x for x in get_field(ser[i], "_locals")]
                # print "dep necesarias para ",i,"--",dep_nec
                dep_imcump = [x for x in get_field(
                    ser[i], "_locals") if x not in ser_order]
                # print "deps imcumplidas",dep_imcump
                if dep_imcump == []:
                    ser_order.append(i)
                    condep.remove(i)
            nivel_dep += 1
        if nivel_dep == 20:
            print("ERROR:there are unresolved dependencies", condep, "-->", dep_imcump)
            exit()
        return ser_order

    def get_imports(self):
        """
        Return two lists of tuples, one (module,class) for all services a other
        for components
        """
        services = [(self.services[s]["module"], self.services[s]["cls"])
                    for s in self.services_order]
        components = [(self.components[s]["module"], self.components[s]["cls"])
                   for s in self.components_order]
        return set(services), set(components)

    def whithout_deps(self, part):
        """
         Return components or services without dependencies
         part can be component or services
        """
        return [x for x in part if not get_field(part[x], "-->")]

    def with_deps(self, part):
        """
         Return components or services with dependencies.
         part can be component or services
        """
        return [x for x in part if get_field(part[x], "-->")]

    def has_remote(self, part, k):
        """
        return true if  k is a remote service or component
        """
        local, remote = self.local_remote(part, k)
        return bool(remote)

    def has_local(self, part, k):
        """
        return true if  k is a local service or component
        """
        local, remote = self.local_remote(part, k)
        return bool(local)

    def local_remote(self, part, k):
        """
        Return two list. Services or Components locals and remotes.
        """
        if "-->" in part[k]:
            local = [x for x in part[k]["-->"]
                     if x.find(self.node["name"] + ".") > -1]
            remote = [x for x in part[k]["-->"]
                      if x.find(self.node["name"] + ".") == -1]
        else:
            local = []
            remote = []
        return local, remote

    @property
    def njson(self):
        return self.conf

    @property
    def node(self):
        return self.conf["node"]

    @property
    def services(self):
        return self.conf["services"]

    @property
    def components(self):
        return self.conf["components"]

    @property
    def robot(self):
        rob = {}
        rob["node"] = self.node
        rob["services"] = self.services
        rob["services_order"] = self.services_order
        rob["components"] = self.components
        rob["components_order"] = self.components_order
        rob["imports"] = self.get_imports()
        return rob

    @services.setter
    def services(self, value):
        self._services = value

    @components.setter
    def components(self, value):
        self._components = value