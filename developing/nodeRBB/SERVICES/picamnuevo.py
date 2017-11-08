#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
import time
import datetime
from nodeRBB.LIBS import control
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import Pyro4
from io import BytesIO

@Pyro4.expose
class picamnuevo(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):
        self.camera =PiCamera()
        self.camera.resolution=(self.width,self.height)
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
        self.camera.vflip = False
        self.buffer=[BytesIO(),BytesIO()]
        self.available=0
        self.lock=1
        super(picamnuevo,self).__init__((self.worker_read,))

    def worker_read(self):

            while self.worker_run:
                self.buffer[self.lock].seek(0)
                self.buffer[self.lock].truncate()
                for foo in self.camera.capture_continuous(self.buffer[self.lock], "jpeg",use_video_port=True):
                    print len(self.buffer[self.lock].getvalue())
                    print self.buffer[self.lock].tell()
                    self.lock,self.available=self.available,self.lock
                time.sleep(self.frec)

    def worker_publ(self):
        while self.worker_run:
            try:
              for k,v in self.subscriptors.iteritems():
                  v.publication(self.buffer[self.available][k])
            except:
              #print("cam dist error")
              pass
    @property
    def image(self):
        #print ("cam %s" % (self.available))
        self.buffer[self.available].seek(0)
        #print size(self.buffer[self.available].read())
        env=self.buffer[self.available].read()
        print type(env)
        print len(env)
        return env

    def subscribe(self,key,uri):
        try:
          self.subscriptors[key]=Pyro4.Proxy(uri)
          print ("arduino subcriptor %s %s" %(key,uri))
          return True
        except:
          return False

if __name__ == "__main__":
    pass
