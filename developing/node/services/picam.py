
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from node.libs import control
from node.libs import utils
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
from io import BytesIO
import Pyro4
import numpy as np
import io
import socket
import struct
import time
import random
import threading


@Pyro4.expose
class picam(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.camera = PiCamera()

        # PiCamera Settings
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = 24
        #self.camera.sharpness = 0
        self.camera.contrast = 0
        self.camera.brightness = 50
        #self.camera.saturation = 0
        #self.camera.ISO = 0
        self.camera.video_stabilization = True
        self.camera.exposure_compensation = 0
        #self.camera.exposure_mode = 'auto'
        #self.camera.meter_mode = 'average'
        #self.camera.awb_mode = 'auto'
        self.camera.image_effect = 'none'
        self.camera.color_effects = None
        self.camera.rotation = 0
        self.camera.hflip = True
        self.camera.vflip = True
        #self.camera.crop = (0.0, 0.0, 1.0, 1.0)

        # Stream settings
        self.buffer = BytesIO()
        self.clients = list()
        self.initPort = 9000

        # TODO: Interface de red automatica
        self.ip = utils.get_ip_address("wlan0")
        super(picam, self).__init__((self.worker_read,))
        #super(picam, self).__init__()

    def worker_read(self):
        while True:
            while (len(self.clients) > 0):  # Si hay clientes a la espera...
                try:
                    for foo in self.camera.capture_continuous(self.buffer, 'jpeg', use_video_port=True):
                        self.acceptConnections()
                        streamPosition = self.buffer.tell()
                        for c in self.clients:
                            if (c.connection is not 0):
                                c.connection.write(
                                    struct.pack('<L', streamPosition))
                                c.connection.flush()
                        self.buffer.seek(0)
                        readBuffer = self.buffer.read()
                        for c in self.clients:
                            if (c.connection is not 0):
                                c.connection.write(readBuffer)
                        self.buffer.seek(0)
                        self.buffer.truncate()
                except Exception as e:
                    if (e.find("Broken") is -1):
                        print "Pipe cerrado"
                finally:
                    for c in self.clients:
                        if (c.connection is not 0):
                            c.connection.write(struct.pack('<L', 0))
                            c.connection.close()
                            c.serverSocket.close()

    def worker_publ(self):
        while self.worker_run:
            try:
                for k, v in self.subscriptors.iteritems():
                    v.publication(self.buffer[self.available][k])
            except:
                #print("cam dist error")
                pass

    @property
    def image(self):
        newClient = ClientSocket(self.initPort + 1)
        self.clients.append(newClient)
        self.initPort = newClient.port
        while not (newClient.waitingForConnection):
            time.sleep(1)
        return self.ip,newClient.port

    def acceptConnections(self):
        # print "Aceptando conexiones desde picamera"
        for c in self.clients:
            c.acceptConnection()

    def subscribe(self, key, uri):
        try:
            self.subscriptors[key] = Pyro4.Proxy(uri)
            print ("arduino subcriptor %s %s" % (key, uri))
            return True
        except:
            return False


class ClientSocket():
    """Class for Clients of PiCamera"""

    def __init__(self, port=9000,):
        self.port = port
        self.serverSocket = socket.socket()
        self.connection = 0
        self.waitingForConnection = False
        self.newPort()

    def newPort(self):
        """Check if a port is available, and if it is, assign it, otherwise continue testing the next one."""
        result = 0
        while (result is 0):
            try:
                print self.port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', self.port))
                if result is 0:
                    self.port += 1
                else:
                    self.serverSocket.bind(('0.0.0.0', self.port))
                    self.serverSocket.listen(0)
                    time.sleep(1)
            except Exception as e:
                utils.format_exception(e)

    def acceptConnection(self):
        """ Accept conections from servers to clients"""
        if self.connection is 0:
            self.waitingForConnection = True
            self.connection = self.serverSocket.accept(
            )[0].makefile("rb" + str(self.port))
            return 0
        else:
            # print "ServerSocket aceptado previamente", self.port
            pass
        return 1

    def getClient(self):
        return self.port, self.serverSocket, self.connection


if __name__ == "__main__":
    pass
