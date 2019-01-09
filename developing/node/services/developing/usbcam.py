#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
import time
from developing.node.libs import control
import cv2
import Pyro4

#TODO: PUBLICATION

@Pyro4.expose
class usbcam(control.Control):
    __REQUIRED = ["width", "height"]
    
    def __init__(self):
        if not hasattr(self, 'framerate'):
                self.framerate = 24
        if not hasattr(self, 'frec'):
                self.frec = 0.01
        self.subscriptors = {}
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.height)
        self.buffer = [0, 0]
        self.available = 0
        self.lock = 1
        self.start_worker(self.worker_read)
        # self.start_publisher(self.__dict__)

    def worker_read(self):
        while self.worker_run:
            retval, self.buffer[self.lock] = self.camera.read()
            self.lock, self.available = self.available, self.lock
            time.sleep(self.frec)


    @property
    def image(self):
        return self.buffer[self.available]

    def subscribe(self, key, uri):
        try:
            self.subscriptors[key] = Pyro4.Proxy(uri)
            print(("arduino subcriptor %s %s" % (key, uri)))
            return True
        except:
            return False


if __name__ == "__main__":
    pass
