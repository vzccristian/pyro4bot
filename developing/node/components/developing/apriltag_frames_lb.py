# ____________developed by cristian vazquez____________________
import time
from node.libs import control
import Pyro4
import cv2
import numpy as np
import io
import picamera
from random import randint

class apriltag_frames_lb(control.Control):
    """Send frames to PiCamera (learnbot)."""
    __REQUIRED = []

    def __init__(self):
        self.detections = None
        self.time_notags = None
        self.init_workers(self.get_frame)
        self.init_workers(self.change_position)


    def get_frame(self):
        stream = io.BytesIO()
        self.deps["pantilt"].move(25,90)
        with picamera.PiCamera() as camera:
            # ----------- DONT USE OPTIONS. ---------------- #
            # camera.vflip = True
            while True:
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                Pyro4.config.SERIALIZER = 'pickle'
                detections = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                    data, openWindow=True)
                if detections:
                    self.deps["ruedas"].set__vel(mi=0, md=0)
                    # target
                    self.detections = detections
                    self.time_notags = None
                    for d in detections:
                        print d["tag_family"], d["tag_id"]
                        corner_l = [d["corners"][0][0], d["corners"][1][0],
                                    d["corners"][2][0], d["corners"][3][0]]
                        # Move pantilt
                        # print d["corners"]
                        pantilt = self.deps["pantilt"].get_pantilt()
                        for c in d["corners"]:
                            if c[0] < 80:
                                self.deps["pantilt"].move(pantilt[0], pantilt[1] + 1)
                                self.deps["ruedas"].set__vel(mi=1000, md=0)
                                time.sleep(0.2)
                                self.deps["ruedas"].set__vel(mi=0, md=0)
                            elif c[0] > 650:
                                self.deps["pantilt"].move(pantilt[0], pantilt[1] - 1)
                                self.deps["ruedas"].set__vel(mi=0, md=1000)
                                time.sleep(0.2)
                                self.deps["ruedas"].set__vel(mi=0, md=0)
                            if c[1] < 80:
                                self.deps["pantilt"].move(pantilt[0] - 2, pantilt[1])
                            elif c[1] > 400:
                                self.deps["pantilt"].move(pantilt[0] + 2, pantilt[1])

                        if c[0] > 80 and c[0] < 650:
                            #   Move base
                            dist_x = max(corner_l) - min(corner_l)
                            if (dist_x < (max(camera.resolution.width, camera.resolution.height) / 4.5) ):
                                # print "LEJOS"
                                self.deps["ruedas"].set__vel(mi=1000, md=1000)
                                if dist_x < 80: time.sleep(2)
                                elif dist_x < 110: time.sleep(1)
                                else: time.sleep(0.5)
                                self.deps["ruedas"].set__vel(mi=0, md=0)
                            # else:
                            #     print "CERCA"

                stream.seek(0)
                stream.truncate()
                time.sleep(self.frec)
            cv2.destroyAllWindows()

    def change_position(self):
        while True:
            time.sleep(self.frec*3)
            if (self.detections is None):
                if self.time_notags is None:  # First time
                    self.time_notags = time.time()
                now = time.time()
                if (now - self.time_notags > 5):
                    self.time_notags = None
                    ranvalue = randint(3, 5)
                    self.deps["ruedas"].set__vel(mi=1000, md=0)
                    time.sleep(ranvalue)
                    self.deps["ruedas"].set__vel(mi=0, md=0)
