import simplejson
import re
import collections


def ascii_encode_dict(data):
    return dict([x.encode('ascii') if isinstance(x, str) else x for x in pair] for pair in data.items())


class MyJson(object):
    def __init__(self, filename, dependencies=False):
        self.json = self.load_json(filename, dependencies)

    def load_json(self, filename, dependencies):
        self.filename = filename if (
                ".json" in filename) else (filename + ".json")
        try:
            data = open(filename).read()
            data = self.del_coments(data)
            data = self.substitute_params(data)
            # method ascii_encode_dict is just for Python 2, Python3 doesn't need that encoding -> it breaks using it.
            json = simplejson.loads(data)
            json = self.load_dependencies(json) if dependencies else json
        except ValueError as e:
            print("ERROR: JSON incorrectly described: " + str(e))
            exit(0)
        except Exception:
            print("ERROR: loading %s" % filename)
        # exit(0)
        return json

    def del_coments(self, data, ch="#"):
        salida = ""
        for line in data.splitlines():
            if line.find(ch) > -1:
                line = line[0:line.find(ch)]
            salida = salida + line + "\n"
        return salida

    def substitute_params(self, data, reg="<.*?>"):
        for match in re.findall(reg, data):
            m = match.replace("<", '"').replace(">", '":')
            data = data.replace(match, self.parameter_value(data, m))
        return data

    def load_dependencies(self, nodo):
        for k, v in nodo.items():
            if type(v) is dict:
                if k.find("(") >= 0 and k.find(")") >= 0:
                    new_file = k[k.find("(") + 1:k.find(")")]
                    hook = self.load_json(new_file)
                    self.dict_merge(hook, v)
                    nodo[k[0:k.find("(")].strip()] = hook
                    del (nodo[k])
                    k = k[0:k.find("(")].strip()
                self.load_dependencies(nodo[k])
            else:
                pass
        return nodo

    def dict_merge(self, dct, merge_dct):
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], collections.Mapping)):
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = self.merge_dct[k]

    def parameter_value(self, data, cad):
        posi = data.find(cad)
        if posi < 0:
            return cad
        else:
            return data[posi + len(cad):data.find("\n", posi)].rstrip(",").strip('"')
