#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
"""
This library inspect packages and get a modude where it defining a classes
his goal is import just classes for  pyro4bot.
"""

import sys
import os
import inspect
import pkgutil
import importlib


def explore_package(module_name):
    """
    Get a list of modules and submodules for a given package
    this function use a recursive algoritm.
    """
    modules = []
    loader = pkgutil.get_loader(module_name)
    for sub_module in pkgutil.walk_packages([loader.path]):
        a, sub_module_name, b = sub_module
        qname = module_name + "." + sub_module_name
        modules.append(qname)
        if b:
            modules.extend(explore_package(qname))
    return modules


def get_clases(m):
    """
    Return a list of classes for a given module
    Warning: if module has non instaled package return a empty list
    """
    list_class = []
    error_class = None
    try:
        mod = importlib.import_module(m)
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            list_class.append(name)
    except Exception as e:
        error_class = e
    return list_class, error_class


def get_packages_not_found(m):
    """
    Return a set of packages for a given module
    Warning: if module has non instaled any package return a empty list
    """
    list_packages = None
    try:
        mod = importlib.import_module(m)
    except Exception as e:
        return "Module " + m + ": " + str(e)

    return None


def get_modules(pkgs):
    """
    Return all modules and submodules for given packages (pkgs).
    """
    if type(pkgs) not in (list, tuple):
        pkgs = (pkgs,)
    return [x for pk in pkgs for x in explore_package(pk)]


def module_class(cls, modules):
    """
    Find a module or modules for a cls class
    if has more than one module return first finded
    """
    modules = [m for m in modules if cls in get_clases(m)]
    return modules[0].lstrip(".node") if len(modules) > 0 else None


def get_all_class(modules):
    clases = {}
    errors = {}
    for m in modules:
        cls, error = get_clases(m)
        if error is not None:
            if m not in errors:
                errors[m] = []
            errors[m] = error
        for cl in cls:
            if cl not in clases:
                clases[cl] = []
            clases[cl].append(m.lstrip(".node"))
    return clases, errors


def import_module(module):
    importlib.import_module(module)


def module_packages_not_found(modules):
    """
    Ŕeturn all modules imported in modules that is no finded
    """
    # return [m for m in modules if pkg in get_packages_not_found(m)]
    x = set()
    for m in modules:
        x.update(get_packages_not_found(m))
    return x


def not_finded_modules(modules_error):
    imports = [x[1].message.split("No module named ")[1] for x
               in list(modules_error.items()) if type(x[1]) is ImportError]

    return list(set(imports))


def show_warnings(modules_errors):
    if modules_errors:
        for k, v in modules_errors.items():
            print(("warning: error in {} --> {}".format(k, v)))

print("INSPECTING MODULES...")
# _modules is a list of all components and services in pyro4bot
# TODO: check if it works
_modules = get_modules(("node.services", "node.components"))
_clases, _modules_errors = get_all_class(_modules)

# it is a list of all modules in system pyro4bot
# TODO: check if it works
_modules_libs = get_modules(("node.libs", "node.node"))
_clases_libs, _modules_libs_errors = get_all_class(_modules_libs)

if __name__ == "__main__":
    pass
