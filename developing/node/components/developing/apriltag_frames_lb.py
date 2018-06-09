# ____________developed by cristian vazquez____________________
import time
from node.libs import control,token, publication
import Pyro4
import cv2
import numpy as np
import io
import picamera
from random import randint

MIN_DIST = 300

class apriltag_frames_lb(control.Control):
    """Send frames to PiCamera (learnbot)."""
    __REQUIRED = []

    def __init__(self):
        self.detections = None
        self.init_time = None
        self.detecteds = {}
        self.newDetection = False
        self.goal = False

        self.ruedas = self.deps["ruedas"] if "ruedas" in self.deps else None
        self.obstaculos = [1000,1000,1000]
        self.start_worker(self.get_laser)
        self.start_worker(self.get_frame)
        self.start_worker(self.change_position)
        self.subscriptors = {}
        self.april_detected = publication.Publication()
        self.start_publisher(self.april_detected,frec=0.1)

    def get_laser(self):
        while True:
            self.obstaculos = self.deps["obstaculos"].get_laser()
            # print self.obstaculos
            time.sleep(self.frec)

    def get_frame(self):
        stream = io.BytesIO()
        self.deps["pantilt"].move(25,90)
        Pyro4.config.SERIALIZER = 'pickle'
        with picamera.PiCamera() as camera:
            # ----------- DONT USE OPTIONS. ---------------- #
            # --- camera.vflip = True ----
            # ----------- DONT USE OPTIONS. ---------------- #
            while not self.goal:
                self.newDetection = False
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                try:
                    self.detections = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                        data, openWindow=True, showInfo=False, name="Learnbot")
                    if self.detections:
                        for d in self.detections:
                            self.saveTag(d)
                    stream.seek(0)
                    stream.truncate()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    print template.format(type(ex).__name__, ex.args)


    def change_position(self):
        while not self.goal:
            if not(self.newDetection):
                self.init_time = time.time()
                self.ruedas.set__vel(mi=1000, md=1000)  # Move
                while ((self.obstaculos[0] > MIN_DIST and self.obstaculos[1] > MIN_DIST and
                        self.obstaculos[2] > MIN_DIST) and
                       time.time() - self.init_time < 10):
                    time.sleep(self.frec*2)
                time.sleep(0.1)
            if not(self.newDetection):
                self.ruedas.set__vel(mi=-1000, md=-1000)
                time.sleep(0.8)
            if not(self.newDetection):
                self.ruedas.set__vel(mi=1000, md=-1000)
                time.sleep(1)
            if not(self.newDetection):
                self.ruedas.set__vel(mi=0, md=0)
                time.sleep(0.1)

    def saveTag(self, april):
        identificator = str(april["tag_family"]) + "." + str(april["tag_id"])
        if (identificator not in self.detecteds):
            self.newDetection = True
            self.ruedas.set__vel(mi=0, md=0)
            if (self.centerPantilt(april)):
                self.ruedas.set__vel(mi=0, md=0)
                self.newDetection = True
                print("--> New tag: {}".format(identificator))
                # self.centerPantilt(april)
                time.sleep(2)
                self.detecteds[identificator] = april
                self.april_detected.update_key_value("aprils", self.detecteds)
                self.deps["pantilt"].move()

    def centerPantilt(self, april):
        centered = True
        pantilt = self.deps["pantilt"] if "pantilt" in self.deps else None
        if pantilt is not None:
            try:
                pan_and_tilt = pantilt.get_pantilt()
                pan = pan_and_tilt[0]
                tilt = pan_and_tilt[1]
            except Exception:
                raise
            for c in april["corners"]:
                if c[0] < 30:
                    tilt += 2
                    centered = False
                if c[0] > 690:
                    centered = False
                    tilt -= 2
                if c[1] < 25:
                    centered = False
                    pan -= 1
                if c[1] > 395:
                    centered = False
                    pan += 1
            pantilt.move(pan, tilt)
        else:
            print "centerPantilt: ERROR in deps."
        return centered

    @Pyro4.expose
    def setGoal(self, value=True):
        self.goal = value

    @Pyro4.expose
    def updateDetecteds(self, value):
        self.detecteds.update(value)
