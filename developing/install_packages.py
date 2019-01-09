#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All datas defined in json configuration are atributes in your code object
"""
This module find in node all paCkages with ImportError and try to INSTALL
with pip module.
"""
import pip
from .node.libs.inspection import _modules_libs_errors, not_finded_modules

print("# PYRO4BOT #")
print("MODULES TO INSTALL:")
modulestointall = not_finded_modules(_modules_libs_errors)
for mod in modulestointall:
    print("\t{}".format(mod))
if not modulestointall:
    print("All packages are up today.")
    exit()

question = input("Do you want install packages? (y/n).. ")

if question.upper() == "Y":
    for mod in modulestointall:
        try:
            pip.main(['install', mod])
        except Exception:
            print("ERROR")
else:
    print("OPS!... AT ANOTHER MOMENT MAYBE?")
