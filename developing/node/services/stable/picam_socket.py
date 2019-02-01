# !/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by cristian vazquez____________________
import time
from node.libs import control
from node.libs import utils
import picamera
from io import BytesIO
import Pyro4
import socket
import struct
import threading


class picam(control.Control):
    """Set a connection socket to the camera."""

    __REQUIRED = ["width", "height", "ethernet"]

    def __init__(self):
        self.camera = PiCamera()

        # PiCamera Settings
        self.camera.resolution = (self.width, self.height)
        if not hasattr(self, 'framerate'):
            self.framerate = 24
        if not hasattr(self, 'frec'):
            self.frec = 0.02

        self.camera.framerate = self.framerate
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.video_stabilization = True
        self.camera.image_effect = 'none'
        self.camera.color_effects = None
        self.camera.rotation = 0

        self.camera.hflip = True if not hasattr(self, 'hflip') else self.hflip
        self.camera.vflip = True if not hasattr(self, 'vflip') else self.vflip

        # self.camera.sharpness = 0
        # self.camera.saturation = 0
        # self.camera.ISO = 0
        # self.camera.sure_compensation = 0
        # self.camera.exposure_mode = 'auto'
        # self.camera.meter_mode = 'average'
        # self.camera.awb_mode = 'auto'
        # self.camera.crop = (0.0, 0.0, 1.0, 1.0)

        # Stream settings
        self.buffer = BytesIO()
        self.clients = list()
        self.initPort = 9000

        self.ip = utils.get_ip_address(self.ethernet)

        self.start_worker(self.worker_read)
        self.start_thread(self.removeClosedConnections)

    def worker_read(self):
        """Main worker."""
        while self.worker_run:
            for foo in self.camera.capture_continuous(self.buffer, 'jpeg', use_video_port=True):
                # Si hay clientes a la espera...
                while len(self.clients) is 0:
                    time.sleep(2)
                try:
                    self.acceptConnections()
                    streamPosition = self.buffer.tell()
                    for c in self.clients:
                        if c.closed is False:
                            try:
                                if c.connection is not 0:
                                    c.connection.write(
                                        struct.pack('<L', streamPosition))
                                    c.connection.flush()
                            except Exception as e:
                                closer = threading.Thread(
                                    target=self.setAsClosed, args=(c,))
                                closer.start()
                    self.buffer.seek(0)
                    readBuffer = self.buffer.read()
                    for c in self.clients:
                        if c.closed is False:
                            try:
                                if c.connection is not 0:
                                    c.connection.write(readBuffer)
                            except Exception as e:
                                closer = threading.Thread(
                                    target=self.setAsClosed, args=(c,))
                                closer.start()
                    self.buffer.seek(0)
                    self.buffer.truncate()
                except Exception as e:
                    utils.format_exception(e)

    @Pyro4.expose
    def image(self):
        """Return IP and PORT to socket connection """
        newClient = ClientSocket(self.initPort + 1)
        self.clients.append(newClient)
        self.initPort = newClient.port
        while not newClient.waitingForConnection:
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
        except Exception:
            pass
        if exception is not None:
            utils.format_exception(exception)

    def removeClosedConnections(self, sec=20):
        """Cleaner. Remove clients marked as closed every "sec" seconds."""
        while self.worker_run:
            time.sleep(sec)
            # print "Antes:", self.clients
            self.clients = [c for c in self.clients if not c.closed]
            # print "Despues:", self.clients


class ClientSocket:
    """Class for Clients of PiCamera"""

    def __init__(self, port=9000, ):
        self.port = port
        self.serverSocket = socket.socket()
        self.connection = 0
        self.closed = False
        self.waitingForConnection = False
        self.newPort()

    def newPort(self):
        """Check if a port is available, and if it is, assign it, otherwise continue testing the next one."""
        result = 0
        while result is 0:
            try:
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
        """ Accept connections from servers to clients"""
        if self.connection is 0:
            print("PICAM-New client: {}".format(self.port))
            self.waitingForConnection = True
            self.connection = self.serverSocket.accept(
            )[0].makefile("rb" + str(self.port))

    def getClient(self):
        """ Return client information"""
        return self.port, self.serverSocket, self.connection

    def setClosed(self):
        """ Set client as closed """
        print("PICAM-Client disconnected: {}".format(self.port))
        self.closed = True
