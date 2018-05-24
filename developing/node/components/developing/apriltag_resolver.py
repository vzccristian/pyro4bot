# ____________developed by cristian vazquez____________________
import time
from node.libs import control
import Pyro4
import cv2
import numpy as np
import io
import socket
import struct
import apriltag
import pickle
import pprint
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

class apriltag_resolver(control.Control):

    def __init__(self):
        self.detector = apriltag.Detector()
        # self.init_workers(self.test)

    @timing
    def test(self):
        time1 = time.time()
        while True:
            cap = cv2.VideoCapture(0)
            while True:
                # Capture frame-by-frame
                ret, frame = cap.read()
                # pprint.pprint(frame)
                if not ret:
                    break
                cv2.imshow("TEST", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                # d = self.get_detections(frame)
                time.sleep(self.frec)

    @Pyro4.expose
    def get_detections(self, frame):
        print("New detect: ", type(frame))
        if self.worker_run:
            if (frame is not None):
                frame = cv2.imdecode(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                detections, dimg = self.detector.detect(gray, return_image=True)


                num_detections = len(detections)

                print 'Detected {} tags.\n'.format(num_detections)

                for i, detection in enumerate(detections):
                    print 'Detection {} of {}:'.format(i + 1, num_detections)
                    print
                    print detection.tostring(indent=2)
                    print

                # Show image
                # window = 'Camera'
                # cv2.namedWindow(window)
                # overlay = frame / 2 + dimg[:, :, None] / 2
                #
                # cv2.imshow(window, overlay)
                # cv2.waitKey(1)

                return str(detections)
            # cv2.destroyAllWindows()
