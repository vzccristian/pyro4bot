
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

"""
JSON_DOCUMENTATION
{SENSOR_NAME} : camera
{c} cls : picam
{c} path : <path>
{c} ethernet : <ethernet>
{m} framerate : 25
{m} width : 640
{m} height : 480
{m} frec : 0.02
{m} worker_run : true
{m} enable : true
END_JSON_DOCUMENTATION
"""

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

        # Cleaner
        self.cleaner = threading.Thread(
            target=self.removeClosedConnections, args=())
        self.cleaner.setDaemon(True)
        self.cleaner.start()

        self.ip = utils.get_ip_address(self.ethernet)

        super(picam, self).__init__((self.worker_read,))

    def worker_read(self):
        """ Main worker"""
        while self.worker_run:
            for foo in self.camera.capture_continuous(self.buffer, 'jpeg', use_video_port=True):
                # Si hay clientes a la espera...
                while (len(self.clients) is 0):
                    time.sleep(0.5)
                try:
                    self.acceptConnections()
                    streamPosition = self.buffer.tell()
                    for c in self.clients:
                        if c.closed is False:
                            try:
                                if (c.connection is not 0):
                                    c.connection.write(
                                        struct.pack('<L', streamPosition))
                                    c.connection.flush()
                            except Exception as e:
                                closer = threading.Thread(target=self.setAsClosed, args=(c,))
                                closer.start()
                    self.buffer.seek(0)
                    readBuffer = self.buffer.read()
                    for c in self.clients:
                        if c.closed is False:
                            try:
                                if (c.connection is not 0):
                                    c.connection.write(readBuffer)
                            except Exception as e:
                                closer = threading.Thread(target=self.setAsClosed, args=(c,))
                                closer.start()
                    self.buffer.seek(0)
                    self.buffer.truncate()
                except Exception as e:
                    utils.format_exception(e)

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
        """Return IP and PORT to socket conection """
        print image
        newClient = ClientSocket(self.initPort + 1)
        self.clients.append(newClient)
        self.initPort = newClient.port
        while not (newClient.waitingForConnection):
            time.sleep(2)
        return self.ip, newClient.port

    def acceptConnections(self):
        """Accept connections from clients"""
        # print "Aceptando conexiones desde picamera"
        for c in self.clients:
            c.acceptConnection()

    def setAsClosed(self, client, exception="None"):
        """Set client as closed"""
        # print "Client: ", client.getClient(), "closing."
        client.setClosed()
        try:
            client.connection.write(struct.pack('<L', 0))
            client.connection.close()
            client.serverSocket.close()
        except:
            pass
        if (exception is not None):
            utils.format_exception(exception)

    def removeClosedConnections(self, sec=20):
        """Cleaner. Remove clients marked as closed every "sec" seconds."""
        while self.worker_run:
            time.sleep(sec)
            # print "Antes:", self.clients
            self.clients = [c for c in self.clients if not c.closed]
            # print "Despues:", self.clients

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
        self.closed = False
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

    def getClient(self):
        """ Return client information"""
        return self.port, self.serverSocket, self.connection

    def setClosed(self):
        """ Set client as closed """
        self.closed = True


if __name__ == "__main__":
    pass
