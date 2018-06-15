# ____________developed by cristian vazquez____________________
import time
from node.libs import control
import Pyro4
import cv2
import apriltag
from itertools import izip
import pprint

CAM = 0

class apriltag_resolver(control.Control):
    __REQUIRED = []

    def __init__(self):
        self.detector = apriltag.Detector()

        # Uncomment to debug with USB-CAM
        # self.start_worker(self.test)

    @Pyro4.expose
    def get_detections(self, frame, picamera=True, openWindow=False, showInfo=False, name="default"):
        try:
            if self.worker_run:
                if (frame is not None):
                    list_detections = []

                    if picamera:
                        frame = cv2.imdecode(frame, 1)

                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    detections, dimg = self.detector.detect(
                        gray, return_image=True)

                    num_detections = len(detections)
                    if (showInfo):
                        print 'Detected {} tags.\n'.format(num_detections)

                    for i, detection in enumerate(detections):
                        list_detections.append(dict(detection._asdict()))
                        if (showInfo):
                            print 'Detection {} of {}:'.format(i + 1, num_detections)
                            print
                            print detection.tostring(indent=2)
                            print

                    if (openWindow):
                        # Show image
                        try:
                            window = 'AprilTag Resolver '+ str(name)
                        except Exception:
                            window = 'AprilTag Resolver'
                        cv2.namedWindow(window)
                        overlay = frame / 2 + dimg[:, :, None] / 2

                        cv2.imshow(window, overlay)
                        cv2.waitKey(1)
                    return list_detections

            if (openWindow):
                cv2.destroyAllWindows()
        except Exception:
            pass

    def test(self, cam_number=CAM):
        while True:
            cap = cv2.VideoCapture(cam_number)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                detections = self.get_detections(frame, picamera=False, openWindow=True, showInfo=True)
                for d in detections:
                    print d["tag_family"], d["tag_id"]
                time.sleep(0.1)
