#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
"""
This library inspect packages and get a modude where it defining a classes
his goal is import just classes for  pyro4bot
"""

import sys
import os
import inspect
import pkgutil
import importlib

def explore_package(module_name):
    """
    get a list of modules and submodules for a given package
    this function use a recursive algoritm
    """
    modules=[]
    loader = pkgutil.get_loader(module_name)
    for sub_module in pkgutil.walk_packages([loader.filename]):
        _, sub_module_name, _ = sub_module
        qname = module_name + "." + sub_module_name
        modules.append(qname)
        modules.extend(explore_package(qname))
    return modules

def get_clases(m,error=False):
    """
    return a list of classes for a given module
    warning: if module has non instaled package return a empty list
    """
    list_class=[]
    try:
        mod = importlib.import_module(m)
        for name, obj in inspect.getmembers(mod,inspect.isclass):
            list_class.append(name)
    except Exception as e:
        if error:
            print("error in {} :{}".format(m,e))
    return list_class

def get_packages_not_found(m,error=False):
    """
    return a set of packages for a given module
    warning: if module has non instaled any package return a empty list
    """
    list_packages=set()
    try:
        mod = importlib.import_module(m)
    except ImportError as e:
        list_packages.add(str(e).split("No module named ")[1])
        #print(e)
    except:
        pass
    return list_packages

def get_modules(pkgs):
    """
    return all modules and submodules for given packages (pkgs)
    """
    if type(pkgs) not in (list, tuple):
        pkgs = (pkgs,)
    return [x for pk in pkgs for x in explore_package(pk) ]

def module_class(cls,modules):
    """
    find a module or modules for a cls class
    if has more than one module return first finded
    """
    modules=[m for m in modules if cls in get_clases(m)]
    return modules[0].lstrip(".node") if len(modules)>0 else None

def import_module(module):
    importlib.import_module(module)

def module_packages_not_found(modules):
    """
    Ŕeturn all modules imported in modules that is no finded
    """
    #return [m for m in modules if pkg in get_packages_not_found(m)]
    x=set()
    for m in modules:
        x.update(get_packages_not_found(m))
    return x

# _modules is a list of all sensors and services in pyro4bot
_modules=get_modules(("node.services","node.sensors"))
# it is a list of all modules in system pyro4bot
_modules_node=get_modules("node")

if __name__ == "__main__":
    pass
    #print(module_class("face",_modules))
    # print(_modules_node)
    # print(module_packages_not_found(_modules_node))
