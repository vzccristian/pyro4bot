#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
import simplejson
import re
import pprint
import collections
import os.path
import utils


def dict_merge(dct, merge_dct):
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def del_coments(data, ch="#"):
    salida = ""
    for line in data.splitlines():
        if (line.find(ch) > -1):
            line = line[0:line.find(ch)]
        salida = salida + line + "\n"
    return salida


def parameter_value(data, cad):
    posi = data.find(cad)
    if posi < 0:
        return cad
    else:
        return data[posi + len(cad):data.find("\n", posi)].rstrip(",").strip('"')


def substitute_params(data, reg="<.*>"):
    for match in re.findall(reg, data):
        m = match.replace("<", '"').replace(">", '":')
        data = data.replace(match, parameter_value(data, m))
    return data


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


def disable_lines(json):
    for key in [x for x in json.keys() if x != "NODE"]:
        for k, v in json[key].items():
            if get_field(v, "enable") == [False]:
                del(json[key][k])
    return json


class MyJson(object):
    def __init__(self, filename):
        self.json = self.load_json(filename)

    def load_json(self, filename):
        if filename.find(".json") < 0:
            filename = filename + ".json"
        try:
            data = open(filename).read()
            data = del_coments(data)
            data = substitute_params(data)
            json = simplejson.loads(data)
            json = self.load_dependencies(json)
        except:
            print("ERROR: loading %s" % (filename))
            raise
            exit(0)
        return json

    def load_dependencies(self, nodo):
        for k, v in nodo.iteritems():
            if type(v) is dict:
                if k.find("(") >= 0 and k.find(")") >= 0:
                    new_file = k[k.find("(") + 1:k.find(")")]
                    hook = self.load_json(new_file)
                    dict_merge(hook, v)
                    nodo[k[0:k.find("(")].strip()] = hook
                    del(nodo[k])
                    k = k[0:k.find("(")].strip()
                self.load_dependencies(nodo[k])
            else:
                pass
        return nodo


class Config:
    def __init__(self, filename="", json=None):
        if json is None:
            json = {}
        if filename == "":
            self.conf = json
        else:
            self.conf = MyJson(filename).json
        self.conf = disable_lines(self.conf)
        self.check_semantic()
        # print self.dependency()
        self.conf["NODE"][self.conf["NODE"]["name"] +
                          ".URI_resolv"] = self.add_uri_conf()

    def check_semantic(self):
        if not self.conf["NODE"].has_key("def_frec"):
            self.conf["NODE"]["def_frec"] = 0.05
        if not self.conf["NODE"].has_key("ip"):
            self.conf["NODE"]["ip"] = utils.get_ip_address(
                self.conf["NODE"]["ethernet"])
            # print self.conf["NODE"]["ethernet"]
            # print utils.get_ip_address(self.conf["NODE"]["ethernet"])
        if not self.conf["NODE"].has_key("name"):
            self.conf["NODE"]["name"] = "node"
        for k, v in self.sensors.items() + self.services.items():
            if not v.has_key("worker_run"):
                v["worker_run"] = True
            if not v.has_key("mode"):
                v["mode"] = "public"
            if not v.has_key("frec"):
                v["frec"] = self.conf["NODE"]["def_frec"]
            if v["cls"].find(".") < 0:
                v["cls"] = v["cls"] + "." + v["cls"]
        error = False
        for m in self.classes():
            if self.module(m) == None:
                print "Module ", m, "dont find"
                error = True
        newservices = {}
        for n in self.services:
            if n.find(".") == -1:
                newservices[self.node["name"] + "." + n] = self.services[n]
            else:
                newservices[n] = self.services[n]
        newrobot = {}
        for n in self.sensors:
            if self.sensors[n].has_key("-->"):
                sp = [self.node["name"] + "." +
                      x for x in self.sensors[n]["-->"] if x.find(".") < 0]
                cp = [x for x in self.sensors[n]["-->"] if x.find(".") >= 0]
                self.sensors[n]["-->"] = sp + cp
            if n.find(".") == -1:
                newrobot[self.node["name"] + "." + n] = self.sensors[n]
            else:
                newrobot[n] = self.sensors[n]
        self.services = newservices
        self.sensors = newrobot
        if error:
            exit()

    def module_cls(self):
        return [self.module(m) for m in self.classes()]

    def module(self, mod_cls):
        """Return directory, module, class  if exist file .py"""
        mod, cls = mod_cls.split(".")
        for d in self.node["path_cls"]:
            if os.path.isfile(self.node["path"] + "/" + d + "/" + mod + ".py"):
                return d, mod, cls
        return None

    def classes(self):
        return list(set(get_field(self.services, "cls") + get_field(self.sensors, "cls")))

    def dependency(self):
        dep_resueltas = [x for x in self.sensors if not get_field(self.sensors[x], "-->")]
        condep = [x for x in self.sensors if get_field(self.sensors[x], "-->")]
        nivel_dep = 0
        while condep and nivel_dep < 20:
            for i in condep:
                dep_nec = [x for x in get_field(self.sensors[i], "-->")]
                # print "dep necesarias para ",i,"--",dep_nec
                dep_imcump = [x for x in get_field(
                    self.sensors[i], "-->") if x not in dep_resueltas]
                # print "deps imcumplidas",dep_imcump
                if dep_imcump == []:
                    dep_resueltas.append(i)
                    condep.remove(i)
            nivel_dep += 1
        if nivel_dep == 20:
            print "ERROR:there are unresolved dependencies", condep, "-->", dep_imcump
            exit()
        else:
            return dep_resueltas

    def whithout_deps(self):
        return [x for x in self.sensors if not get_field(self.sensors[x], "-->")]

    def has_remote(self, k):
        local, remote = self.local_remote(k)
        return bool(remote)

    def has_local(self, k):
        local, remote = self.local_remote(k)
        return bool(local)

    def local_remote(self, k):
        local = [x for x in self.sensors[k]["-->"]
                 if x.find(self.node["name"] + ".") > -1]
        remote = [x for x in self.sensors[k]["-->"]
                  if x.find(self.node["name"] + ".") == -1]
        return local, remote

    def with_deps(self):
        return [x for x in self.sensors if get_field(self.sensors[x], "-->")]

    def with_local_deps(self):
        deps = [x for x in self.sensors if get_field(
            self.sensors[x], "-->") and self.has_local(x)]
        return deps

    def with_remote_deps(self):
        deps = [x for x in self.sensors.keys() if get_field(
            self.sensors[x], "-->") and self.has_remote(x)]
        # print deps
        return deps

    def add_uri_conf(self):
        conf = {}
        conf["cls"] = "uriresolver.uriresolver"
        conf["ip"] = self.conf["NODE"]["ip"]
        conf["start_port"] = self.conf["NODE"]["start_port"]
        conf["port_node"] = self.conf["NODE"]["port_node"]
        conf["port_ns"] = self.conf["NODE"]["port_ns"]
        conf["mode"] = "local"
        conf["basename"] = self.conf["NODE"]["name"]

        return conf

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
        r = self.conf["services"]
        r.update(self.conf["sensors"])
        return r


# Main function
# if __name__ == "__main__":
