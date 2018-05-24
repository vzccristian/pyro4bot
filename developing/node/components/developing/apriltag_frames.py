# ____________developed by cristian vazquez____________________
import time
from node.libs import control
import Pyro4
import cv2
import numpy as np
import io
import socket
import struct
import pickle
import picamera
import picamera.array


class apriltag_frames(control.Control):
    __REQUIRED = ["height", "width"]

    def __init__(self):
        self.num_detections = 0
        self.detection = None
        self.init_workers(self.get_frame)

    def get_frame(self):
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            # DONT USE OPTIONS.
            # camera.resolution = (self.height, self.width)
            # camera.framerate = 60
            # camera.video_stabilization = True
            # camera.image_effect = 'none'
            # camera.color_effects = None
            # camera.rotation = 0
            # camera.vflip = True
            while True:
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                Pyro4.config.SERIALIZER='pickle'
                d = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                    data)
                print("DETECTED: {}".format(d))
                # img = cv2.imdecode(data, 1)
                # cv2.imshow('frame', img)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                # reset the stream before the next capture
                stream.seek(0)
                stream.truncate()
                time.sleep(self.frec)
            cv2.destroyAllWindows()
