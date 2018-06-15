90  # ____________developed by cristian vazquez____________________
import time
from node.libs import control, publication
import cv2
import numpy as np
import io
import picamera
import Pyro4

class apriltag_frames_ab(control.Control):
    """Send frames to PiCamera (Alphabot)."""
    __REQUIRED = []

    def __init__(self):
        self.detections = None
        self.init_time = None
        self.detecteds = []
        self.aprils = []
        self.newDetection = False
        self.goal = False

        self.ruedas = self.deps["ruedas"] if "ruedas" in self.deps else None
        self.start_worker(self.get_frame)
        self.start_worker(self.change_position_with_ir)

        self.subscriptors = {}
        self.april_detected = publication.Publication()
        self.start_publisher(self.april_detected, frec=0.5)


    def get_frame(self):
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            # ----------- DONT USE OPTIONS. ---------------- #
            # --- camera.vflip = True ----
            # ----------- DONT USE OPTIONS. ---------------- #
            while not self.goal:
                print("DETECTEDS[{}]: {}".format(len(self.detecteds), self.detecteds))
                print("APRILS[{}]: {}".format(len(self.aprils), self.aprils))
                # print("SUBS: {}".format(self.subscriptors))
                self.newDetection = False
                camera.capture(stream, format='jpeg', use_video_port=True)
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                Pyro4.config.SERIALIZER = 'pickle'
                try:
                    self.detections = self.deps["pc_apriltag.apriltag_resolver"].get_detections(
                        data, openWindow=True, showInfo=False, name="Alphabot")
                    if self.detections:
                        for d in self.detections:
                            self.saveTag(d)
                    stream.seek(0)
                    stream.truncate()
                    time.sleep(self.frec)
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    print template.format(type(ex).__name__, ex.args)
                    time.sleep(2)

                if len (self.aprils) == self.numero_marcas:
                    print "------------------------------------------"
                    print "---->   TARGET REACHED   <----"
                    print self.aprils
                    print "------------------------------------------"
                    self.deps["ruedas"].setvel(0, 0)
                    self.goal = True

    def change_position_with_ir(self):
        obstaculos = self.deps["obstaculos"] if "obstaculos" in self.deps else None
        ultrasonido = self.deps["alphaultrasound"] if "alphaultrasound" in self.deps else None
        if obstaculos is not None and ultrasonido is not None and self.ruedas is not None:
            time.sleep(1)
            while not self.goal:
                if not(self.newDetection):
                    self.init_time = time.time()
                    self.ruedas.setvel(100, 100, True, True)  # Move
                    distance = ultrasonido.getDistance()
                    infrarrojos = obstaculos.get_ir()
                    # print "0[{}] - DIST: {} - INFRAROJOS: {},{}".format(self.newDetection, distance, infrarrojos[0], infrarrojos[1])
                    while (distance > 40 and infrarrojos[0] == 1 and
                           infrarrojos[1] == 1 and not(self.newDetection) and
                           time.time() - self.init_time < 12):
                        distance = ultrasonido.getDistance()
                        infrarrojos = obstaculos.get_ir()
                        # print "1[{}] - DIST: {} - INFRAROJOS: {},{}".format(self.newDetection, distance, infrarrojos[0], infrarrojos[1])
                        time.sleep(self.frec)
                    # print "2[{}] - DIST: {} - INFRAROJOS: {},{}".format(self.newDetection, distance, infrarrojos[0], infrarrojos[1])
                    self.ruedas.setvel(0, 0)
                    time.sleep(0.1)
                    if (not self.newDetection and not self.goal):
                        self.ruedas.setvel(100, 100, False, False)
                        time.sleep(0.5)
                    if (not self.newDetection and not self.goal):
                        self.ruedas.setvel(100, 100, True, False)
                        time.sleep(0.4)
                    if (not self.newDetection and not self.goal):
                        self.ruedas.setvel(0, 0)
                        time.sleep(0.1)
        else:
            print "change_position_with_ir: ERROR in deps."

    def saveTag(self, april):
        identificator = str(april["tag_family"]) + "." + str(april["tag_id"])
        if (identificator not in self.detecteds and identificator not in self.aprils):
            self.newDetection = True
            self.ruedas.setvel(0, 0)
            if (self.centerPantilt(april)):
                self.ruedas.setvel(0, 0)
                self.newDetection = True
                print("--> New tag: {}".format(identificator))
                self.centerPantilt(april)
                time.sleep(2)
                self.detecteds.append(identificator)
                self.april_detected.update_key_value("aprils", self.detecteds)

    def centerPantilt(self, april):
        # print "centerPantilt ", april
        centered = True
        pantilt = self.deps["alphapantilt"] if "alphapantilt" in self.deps else None
        if pantilt is not None:
            try:
                pan_and_tilt = pantilt.get_pantilt()
                pan = pan_and_tilt[0]
                tilt = pan_and_tilt[1]
            except Exception:
                raise
            for c in april["corners"]:
                # print "x:", c[0], " y:", c[1]
                if c[0] < 40:
                    pan -= 2
                    centered = False
                if c[0] > 680:
                    centered = False
                    pan += 2
                if c[1] < 30:
                    centered = False
                    tilt += 1
                if c[1] > 390:
                    centered = False
                    tilt -= 1
            pantilt.set_pantilt(pan, tilt)
        else:
            print "centerPantilt: ERROR in deps."
        if centered:
            pantilt.set_pantilt() # Default
        return centered

    def change_position(self):
        print "change_position working"
        ultrasonido = self.deps["alphaultrasound"] if "alphaultrasound" in self.deps else None
        self.ruedas = self.deps["ruedas"] if "ruedas" in self.deps else None
        if ultrasonido is not None and self.ruedas is not None:
            time.sleep(1)
            while not self.goal:
                if not(self.newDetection):
                    self.init_time = time.time()
                    self.ruedas.setvel(100, 100, True, True)  # Move
                    distance = ultrasonido.getDistance()
                    print "0[{}] - DIST: {} ".format(self.newDetection, distance)
                    while (distance > 40 and not(self.newDetection) and
                           time.time() - self.init_time < 10):
                        distance = ultrasonido.getDistance()
                        print "1[{}] - DIST: {} ".format(self.newDetection, distance)
                        time.sleep(self.frec)
                    print "2[{}] - DIST: {} ".format(self.newDetection, distance)
                    self.deps["ruedas"].setvel(0, 0)
                    time.sleep(0.1)
                    if not(self.newDetection):
                        self.ruedas.setvel(100, 100, False, False)
                        time.sleep(0.8)
                    if not(self.newDetection):
                        self.ruedas.setvel(100, 100, True, False)
                        time.sleep(1)
                    if not(self.newDetection):
                        self.ruedas.setvel(0, 0)
                        time.sleep(0.1)
        else:
            print "change_position: ERROR in deps."

    @Pyro4.expose
    def updateAprils(self, value):
        if value not in self.aprils:
            self.aprils.append(value)
