#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4

"""
JSON_DOCUMENTATION
{SENSOR_NAME} : < SENSOR NAME >
{c} cls : < CLASS NAME >
{d} --> : [ DEPENDENCIES ]
{m} ATRIBUTE1 : < VALUE >
{m} frec : 0.02
{m} worker_run : true
{m} enable : true
END_JSON_DOCUMENTATION
"""


class < CLASS NAME > (control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        # Atribute example
        self.value = 0

        # Worker example
        self.init_workers(self.worker)

        # Subscription example
        #  self.send_subscripcion(self.usbserial, "LASER")

        # Publication example
        # self.buffer = token.Token()
        # self.buffer.update_key_value("value", self.value)
        # self.init_publisher(self.buffer)

    def worker(self):
        while self.worker_run:
            print(".")
            # write here code for your sensor thread

    # here your methods
    # Expose your method to exterior with decorator @Pyro4.expose
    @Pyro4.expose
    def get_value(self):
        return self.value
