import time
from node.libs import control
import Pyro4
import pprint


class apriltag_subscripter(control.Control):
    __REQUIRED = []

    def __init__(self):
        self.aprils = []
        self.start_subscription("*.apriltag", "aprils", "aprils", self.botname)
        self.start_worker(self.worker)

    def worker(self):
        while self.worker_run:
            # print("subs{}-aprils{}: {}".format(len(self.deps["*.apriltag"]), len(self.aprils), self.aprils))
            # print "deps",len(self.deps["*.apriltag"]), self.deps["*.apriltag"]
            for a in self.aprils:
                for dp in self.deps["*.apriltag"]:
                    dp.updateAprils(a)
            time.sleep(self.frec)
