#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import threading

# TODO: Prevenir desconexiones remotadas una vez conectado.

class RemoteCamera (control.Control):

    def __init__(self):
        # Worker example
        self.init_workers(self.worker)

        # Subscription example
        #  self.send_subscripcion(self.usbserial, "LASER")

        # Publication example
        # self.buffer = token.Token()
        # self.buffer.update_key_value("value", self.value)
        # self.init_publisher(self.buffer)

    def worker(self):
        print("\n\nWorker is running.")
        while self.worker_run:
            for k in self.deps.keys():
                print("Connected to: {}".format(self.deps[k].get_pyroid()))
                print("Handshake: {}".format(self.deps[k]._pyroHandshake))
            time.sleep(self.frec)
            # write here code for your sensor thread

    # here your methods
    # Expose your method to exterior with decorator @Pyro4.expose
    @Pyro4.expose
    def get_value(self):
        return self.value
