#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
"""
This module find in node all pagakages with ImportError and try to INSTALL
with pip module.

"""
from imp import find_module
from node.libs.inspection import _modules_libs_errors, not_finded_modules
import pip

print("MODULES TO INSTALL:")
modulestointall = not_finded_modules(_modules_libs_errors)
for mod in modulestointall:
    print ("    {}".format(mod))
if not modulestointall:
    print("All pakages are up today")
    exit()
question = raw_input("Do you want install pagakages? (Y/N).. ")

if question.upper() == "Y":
    for mod in modulestointall:
        try:
            pip.main(['install', mod])
        except Exception:
            print("ERROR IN INSTALL")
else:
    print("OPPS... AT ANOTHER MOMENT MAYBE?")
