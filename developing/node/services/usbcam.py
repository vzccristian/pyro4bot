#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
import time
from node.libs import control
import cv2
import Pyro4


@Pyro4.expose
class usbcam(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.subscriptors = {}
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.height)
        self.buffer = [0, 0]
        self.available = 0
        self.lock = 1
        #super(usbcam, self).__init__()
        self.init_workers(self.worker_read)

    def worker_read(self):
        while self.worker_run:
            retval, self.buffer[self.lock] = self.camera.read()
            self.lock, self.available = self.available, self.lock
            time.sleep(self.frec)

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
        #print ("cam %s" % (self.available))
        return self.buffer[self.available]

    def subscribe(self, key, uri):
        try:
            self.subscriptors[key] = Pyro4.Proxy(uri)
            print("arduino subcriptor %s %s" % (key, uri))
            return True
        except:
            return False


if __name__ == "__main__":
    pass
