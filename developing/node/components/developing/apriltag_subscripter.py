import time
from node.libs import control
import Pyro4
import pprint


class apriltag_subscripter(control.Control):
    __REQUIRED = []

    def __init__(self):
        self.aprils = {}
        self.init_workers(self.worker)
        self.send_subscription(self.subscribeTo1, "aprils", self.botname)
        # self.send_subscription(self.subscribeTo2, "aprils", self.botname)

    def worker(self):
        while self.worker_run:
            print "apriltag_subscripter", self.aprils
            time.sleep(self.frec)
