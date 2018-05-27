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
                    data, openWindow=True)
                self.detections = detections
                if detections:
                    for d in detections:
                        print d["tag_family"], d["tag_id"]
                        corner_l = [d["corners"][0][0], d["corners"][1][0],
                                    d["corners"][2][0], d["corners"][3][0]]
                        dist_x = max(corner_l) - min(corner_l)
                        if (dist_x < ((max(camera.resolution.width, camera.resolution.height) / 2.5) - 20)):
                            print "LEJOS"
                            self.deps["ruedas"].set__vel(mi=1000, md=1000)
                            print dist_x
                            if dist_x < 40:
                                print "3.5"
                                time.sleep(3.5)
                            elif dist_x < 75:
                                print "3"
                                time.sleep(3)
                            elif dist_x < 100:
                                print "2"
                                time.sleep(2)
                            else:
                                print "1"
                                time.sleep(1)
                            self.deps["ruedas"].set__vel(mi=0, md=0)
                        else:
                            print "CERCA"

                stream.seek(0)
                stream.truncate()
                time.sleep(self.frec)
            cv2.destroyAllWindows()
