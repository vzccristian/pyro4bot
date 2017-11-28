
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from nodeRBB.LIBS import control
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
class picam(control.control):
    @control.loadconfig
    def __init__(self, data, **kwargs):
        self.camera = PiCamera()
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
        self.buffer = BytesIO()
        self.clients = list()
        self.available = 0
        self.lock = 1
        self.initPort = 9000
        super(picam,self).__init__((self.worker_read,))
        #super(picam, self).__init__()


    def worker_read(self):
        while True:
            while (len(self.clients) > 0):  # Si hay clientes a la espera...
                try:
                    for foo in self.camera.capture_continuous(self.buffer, 'jpeg', use_video_port=True):
                        self.acceptConnections()
                        print self.clients
                        #for c in range(len(self.clients)-1, -1, -1):
                        for c in self.clients:
                            c[2].write(struct.pack('<L', self.buffer.tell()))
                            c[2].flush()
                        self.buffer.seek(0)
                        #for c in range(len(self.clients)-1, -1, -1):
                        for c in self.clients:
                            c[2].write(self.buffer.read())
                        self.buffer.seek(0)
                        self.buffer.truncate()
                finally:
                    for c in self.clients:
                        c[2].write(struct.pack('<L', 0))
                        c[2].close()
                        c[1].close()

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
        sv = socket.socket()
        port = self.initPort + 1
        # Checking if port is available
        result = 0
        while (result == 0):
            print "Testing port " + str(port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            print result
            if result == 0:
                print "Port isnt available."
                port += 1
            else:
                print "Port is available."
                self.initPort = port
                sv.bind(('0.0.0.0', port))
                sv.listen(0)
                self.clients.append([port, sv, 0])
                time.sleep(2)

        return port


    def acceptConnections(self):
        for c in self.clients:
            if (c[2]==0):
                print "Accepting connection:", c[0]
                c[2] = c[1].accept()[0].makefile("rb"+str(c[0]))
                print self.clients


    def subscribe(self, key, uri):
        try:
            self.subscriptors[key] = Pyro4.Proxy(uri)
            print ("arduino subcriptor %s %s" % (key, uri))
            return True
        except:
            return False


if __name__ == "__main__":
    pass
