import time
from node.libs import control
import Pyro4



class apriltag_subscripter(control.Control):
    __REQUIRED = []

    def __init__(self):
        self.aprils = []
        self.start_subscription(self.subscribeTo1, self.topic, self.topic, self.botname)
        self.start_subscription(self.subscribeTo2, self.topic, self.topic, self.botname)
        self.start_worker(self.worker)

    def worker(self):
        # print self.deps
        while self.worker_run:
            # print "aprils", self.aprils
            for a in self.aprils:
                self.deps["apriltag"].updateDetecteds(a)
            if (len(self.aprils) > 3):
                 self.deps["apriltag"].setGoal()
                 self.worker_run = False
            time.sleep(self.frec)
