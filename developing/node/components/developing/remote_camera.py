#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
import threading


class RemoteCamera (control.Control):

    def __init__(self):
        # Worker example
        self.init_workers(self.worker)

    def worker(self):
        print("\n\nWorker is running.")
        while self.worker_run:
            for k in self.deps.keys():
                print("Connected to: {}".format(self.deps[k].get_pyroid()))
                print("Handshake: {}".format(self.deps[k]._pyroHandshake))
            time.sleep(self.frec)
