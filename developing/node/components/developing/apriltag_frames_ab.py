# ____________developed by cristian vazquez____________________
import time
from node.libs import control, token
import Pyro4
import cv2
import numpy as np
import io
import picamera

class apriltag_frames_ab(control.Control):
    """Send frames to PiCamera (Alphabot)."""
    __REQUIRED = []

    def __init__(self):
        self.detections = None
        self.time_notags = None
        self.detecteds = {}



        self.init_workers(self.get_frame)
        self.init_workers(self.change_position)

        self.subscriptors = {}
        self.april_detected = token.Token()
        self.init_publisher(self.april_detected,)

    def get_frame(self):
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            # ----------- DONT USE OPTIONS. ---------------- #
            # camera.vflip = True
            while True:
                print "SUBS:", self.subscriptors
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                Pyro4.config.SERIALIZER = 'pickle'
                try:
                    self.detections = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                        data, openWindow=True)
                    if self.detections:
                        self.deps["ruedas"].setvel(0, 0)
                        for d in self.detections:
                            self.comunicate(d)
                    stream.seek(0)
                    stream.truncate()
                    time.sleep(self.frec)
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    print template.format(type(ex).__name__, ex.args)
                    time.sleep(2)
            cv2.destroyAllWindows()

    def change_position(self):
        while True:
            time.sleep(self.frec * 5)
            if (self.detections is None):
                if self.time_notags is None:  # First time
                    self.time_notags = time.time()
                now = time.time()
                if (now - self.time_notags > 5):
                    self.time_notags = None
                    self.deps["ruedas"].setvel(99,99,True,False)
                    time.sleep(0.5)
                    self.deps["ruedas"].setvel(0, 0)

    def comunicate(self, april):
        if (april["tag_family"] not in self.detecteds):
            print("Adquired: ", april["tag_family"])
            self.detecteds[april["tag_family"]] = april
            self.april_detected.update_key_value("aprils", self.detecteds)
            print "SUBS:", self.subscriptors
