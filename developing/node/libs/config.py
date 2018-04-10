#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
import os.path
import utils
import myjson
from inspection import _modules, _modules_errors, _clases, import_module
from termcolor import colored


def get_field(search_dict, field, enable=True):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []
    for key, value in search_dict.iteritems():
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
        if json is None:
            json = {}
        self.conf = json if (filename == "") else myjson.MyJson(
            filename, dependencies=True).json
        self.disable_lines()
        self.check_semantic()
        self.services_order = self.dependency(self.services)
        self.sensors_order = self.dependency(self.sensors)
        # print(self.sensors_order)
        # print(self.services_order)
        # print(self.sensors)
        # print(self.services)
        # exit()
        #self.conf["NODE"][self.conf["NODE"]["name"] +
        #                  ".URI_resolv"] = self.add_uri_conf

    def disable_lines(self):
        for key in [x for x in self.conf.keys() if x != "NODE"]:
            for k, v in self.conf[key].items():
                if get_field(v, "enable") == [False]:
                    del(self.conf[key][k])

    def check_semantic(self):
        if "def_frec" not in self.conf["NODE"]:
            self.conf["NODE"]["def_frec"] = 0.05

        if "ip" not in self.conf["NODE"]:
            self.conf["NODE"]["ip"] = utils.get_ip_address(
                self.conf["NODE"]["ethernet"])
        if "name" not in self.conf["NODE"]:
            self.conf["NODE"]["name"] = "node"

        for k, v in self.sensors.items() + self.services.items():
            if "worker_run" not in v:
                v["worker_run"] = True
            if "mode" not in v:
                v["mode"] = "public"
            if "frec" not in v:
                v["frec"] = self.conf["NODE"]["def_frec"]
            v["docstring"] = {}
            v["exposed"] = {}
        for k, v in self.services.items():
            v["mode"] = "local"

        newservices = {}
        for n in self.services:
            if _clases.get(self.services[n]["cls"], None) is not None:
                if len(_clases[self.services[n]["cls"]]) > 1:
                    print("Warning: there are many modules {} for class {}".format(
                        _clases[self.services[n]["cls"]], self.services[n]["cls"]))
                self.services[n]["module"] = _clases[self.services[n]["cls"]][0]
                if "." not in n:
                    newservices[self.node["name"] + "." + n] = self.services[n]
                else:
                    newservices[n] = self.services[n]
            else:
                print(colored("ERROR: Class {} not found or error in Modules".format(
                    self.services[n]["cls"]), "red"))
                for k_error, error in _modules_errors.iteritems():
                    print("Module {}: {}".format(k_error, error))
                exit()
            if ("-->") in self.services[n]:
                sp = [self.node["name"] + "." +
                      x for x in self.services[n]["-->"] if x.find(".") < 0]
                cp = [x for x in self.services[n]["-->"] if x.find(".") >= 0]
                self.services[n]["-->"] = sp + cp  # esto se puede simplificar

        self.services = newservices
        newrobot = {}
        for n in self.services:
            self.services[n]["_locals"] = []
            self.services[n]["_resolved_remote_deps"] = []
            if "-->" in self.services[n]:
                self.services[n]["_locals"], self.services[n]["_resolved_remote_deps"] = self.local_remote(
                    self.services, n)

        for n in self.sensors:
            if _clases.get(self.sensors[n]["cls"], None) is not None:
                if len(_clases[self.sensors[n]["cls"]]) > 1:
                    print("Warning: there are many modules {} for class {}".format(
                        _clases[self.sensors[n]["cls"]], self.sensors[n]["cls"]))
                self.sensors[n]["module"] = _clases[self.sensors[n]["cls"]][0]
            else:
                print(colored("ERROR: Class {} not found or error in Modules".format(
                    self.sensors[n]["cls"]), "red"))
                for k_error, error in _modules_errors.iteritems():
                    print("Module {}: {}".format(k_error, error))
                exit()
            self.sensors[n]["_services"] = list(self.services)
            if ("-->") in self.sensors[n]:
                sp = [self.node["name"] + "." +
                      x for x in self.sensors[n]["-->"] if x.find(".") < 0]
                cp = [x for x in self.sensors[n]["-->"] if x.find(".") >= 0]
                self.sensors[n]["-->"] = sp + cp  # esto se puede simplificar
            if n.find(".") == -1:
                newrobot[self.node["name"] + "." + n] = self.sensors[n]
            else:
                newrobot[n] = self.sensors[n]

        self.sensors = newrobot
        for n in self.sensors:
            self.sensors[n]["_locals"] = []
            self.sensors[n]["_resolved_remote_deps"] = []
            if "-->" in self.sensors[n]:
                self.sensors[n]["_locals"], self.sensors[n]["_resolved_remote_deps"] = self.local_remote(
                    self.sensors, n)
                # print("REMO:",self.sensors[n]["_resolved_remote_deps"])

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
            print "ERROR:there are unresolved services dependencies", condep, "-->", dep_imcump
            exit()
        return ser_order

    def get_imports(self):
        """
        Return two lists of tuples, one (module,class) for all services a other
        for sensors
        """
        services = [(self.services[s]["module"], self.services[s]["cls"])
                    for s in self.services_order]
        sensors = [(self.sensors[s]["module"], self.sensors[s]["cls"])
                   for s in self.sensors_order]
        return set(services), set(sensors)

    def whithout_deps(self, part):
        """
         Return sensors or services whihout dependencies
         part can be sensor or services
        """
        return [x for x in part if not get_field(part[x], "-->")]

    def with_deps(self, part):
        """
         Return sensors or services whih dependencies.
         part can be sensor or services
        """
        return [x for x in part if get_field(part[x], "-->")]

    def has_remote(self, part, k):
        """
        return true if  k is a remote service or sensor
        """
        local, remote = self.local_remote(part, k)
        return bool(remote)

    def has_local(self, part, k):
        """
        return true if  k is a local service or sensor
        """
        local, remote = self.local_remote(part, k)
        return bool(local)

    def local_remote(self, part, k):
        """
        return two list. services or sensors locals and remotes
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

    # def add_uri_conf(self):
    #     conf = {}
    #     conf["cls"] = "uriresolver"
    #     conf["ip"] = self.conf["NODE"]["ip"]
    #     conf["start_port"] = self.conf["NODE"]["start_port"]
    #     conf["port_node"] = self.conf["NODE"]["port_node"]
    #     conf["port_ns"] = self.conf["NODE"]["port_ns"]
    #     conf["mode"] = "local"
    #     conf["basename"] = self.conf["NODE"]["name"]
    #     return conf

    @property
    def njson(self):
        return self.conf

    @property
    def node(self):
        return self.conf["NODE"]

    @property
    def services(self):
        return self.conf["services"]

    @property
    def sensors(self):
        return self.conf["sensors"]
