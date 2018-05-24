# ____________developed by cristian vazquez____________________
import time
from node.libs import control
import Pyro4
import cv2
import numpy as np
import io
import picamera


class apriltag_frames(control.Control):
    __REQUIRED = []

    def __init__(self):
        self.init_workers(self.get_frame)
        self.detections = None

    def get_frame(self):
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            # ----------- DONT USE OPTIONS. ---------------- #
            # camera.vflip = True
            while True:
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                Pyro4.config.SERIALIZER = 'pickle'
                detections = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                    data)
                self.detections = detections
                if detections:
                    for d in detections:
                        print d["tag_family"], d["tag_id"]
                stream.seek(0)
                stream.truncate()
                time.sleep(self.frec)
            cv2.destroyAllWindows()
