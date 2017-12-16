import Pyro4
import Pyro4.naming as nm
import utils
import sys
import threading
from termcolor import colored
import time

INTERFACE = "wlan0"


def printThread(color="green"):
    return ((colored("[" + threading.current_thread().getName() + "]", color)))


class bigbrother (object):
    def __init__(self, ethernet="wlan0"):
        if (ethernet is not "wlan0"):
            INTERFACE = ethernet
        self.ns = ""  # Thread
        self.nameServerWorking = False
        self.nameserver = ""
        self.start()

    def start(self):
        print printThread(color="red"), "--> Checking name_server"
        try:
            # Working
            ns = Pyro4.locateNS()
        except:
            self.nameServerWorking = True
            self.ns = threading.Thread(target=self.createNameServer, args=())
            self.ns.start()


    def createNameServer(self):
        print printThread(), "--> Creating new name server on:", colored(INTERFACE, "magenta")
        try:
            self.nameserver=nm.startNSloop(host=utils.get_ip_address(INTERFACE))
        except:
            raise

    def test(self):
        print "test"

    def list(self):
        print "List Nameserver"
        # TODO
        # self.nameserver.nm.NameServer.list()


    def execute(self,command):
        return {
            'list': self.list,
            'test' : self.test,
        }.get(command,"Error")


if __name__ == "__main__":
    threading.current_thread().setName("Main")
    if len(sys.argv) > 1:
        INTERFACE = sys.argv[1]
    bb = bigbrother(ethernet=INTERFACE)

    while (bb.nameServerWorking):
        time.sleep(1)
        command = raw_input("\n"+colored("Comando a la espera: ","yellow"))
        try:
            realCommand=bb.execute(command)
            if (realCommand is not "Error"):
                realCommand()
        except:
            raise
            print (colored("Comando erroneo","red"))

    if (bb.nameServerWorking):
        bb.ns.join()

    print printThread(color="red"), "Saliendo..."
