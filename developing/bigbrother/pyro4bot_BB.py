import Pyro4
import Pyro4.naming as nm
import utils
import sys

INTERFACE = "wlan0"

class bigbrother (object):
    def __init__(self,ethernet="wlan0"):
        if (ethernet is not "wlan0"):
            INTERFACE = ethernet
        self.start()

    def start(self):
        print "Checking name_server"
        try:
            # Working
            ns = Pyro4.locateNS()
        except:
            self.createNameServer()
            # Not working

    def createNameServer(self):
        print "Creating new name server on:", INTERFACE
        try:
            nm.startNS(host=utils.get_ip_address(INTERFACE))
        except:
            raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print sys.argv[1]
        INTERFACE = sys.argv[1]
    bb = bigbrother(ethernet=INTERFACE)
