#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
import time
from node.libs import control, utils, token
from node.libs.bluetooth import bt_RFCOMM
import simplejson as json
import Pyro4


@Pyro4.expose
class bluetooth_serial(control.Control):
    __REQUIRED = ["Port"]

    def __init__(self):
        self.subscriptors = {}
        self.buffer = publication.Publication()()
        self.writer = []
        self.clients = {}
        self.devices = None
        self.data = None
        self.server = bt_RFCOMM.BTServer(self.Port)
        self.start_thread(self.server.clients_accept)
        self.start_worker(self.worker_reader)
        self.start_worker((self.Discover,))
        #self.start_publisher(self.buffer,)

    def worker_reader(self):
        while self.worker_run:
            clients = self.server.clients.copy()
            for cli in clients:
                self.data =(cli,self.server.get_data(cli))
                if self.data is not None:
                    print(("RECEV: ",self.data))
            #time.sleep(self.frec)


    def Discover(self):
        self.devices=self.server.discover_devices()
        print(self.devices)
        print(("MAC: ",self.server.mac))


    def sendMessageTo(self,mac,msg):
      self.server.sendData(mac,msg)
