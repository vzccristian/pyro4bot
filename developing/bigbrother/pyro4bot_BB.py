import Pyro4
import Pyro4.naming as nm
import utils
from utils import printThread as printT
import sys
import threading
import time
import sched
from termcolor import colored
import signal
import subprocess

PROXY_AND_NS_PASSWORD = "PyRobot"
PROXY_PORT = 6060
PROXY_INTERFACE = "wlan1"
""" Class for NS gestion """
class bigbrother(object):
    def __init__(self, _pyro4ns):
        self.pyro4ns = _pyro4ns  # Pyro4NS location

        self.bigBrother = sched.scheduler(time.time, time.sleep)  # bigBrother
        self.bigBrother.enter(5, 1, self.update, (self.pyro4ns,))  # bigBrother
        self.thread_bigBrother = threading.Thread(
            target=self.bigBrother.run, args=())
        self.thread_bigBrother.setDaemon(1)
        self.thread_bigBrother.start()

        self.thread_proxy = threading.Thread(
            target=self.createPyroProxy, args=())
        self.thread_proxy.setDaemon(1)
        self.thread_proxy.start()

        # Data treatment
        self.robots = {}
        self.sensors = {}

    def update(self, pyro4ns):
        self.robots = {x: self.pyro4ns.list(
        )[x] for x in self.pyro4ns.list() if x not in "Pyro.NameServer"}
        for key, value in self.robots.iteritems():
            robot_uris = self.proxy(key).get_uris()
            for u in robot_uris:
                currentSensor = u.split(".")[1].split("@")[0]
                if type(self.sensors.get(currentSensor)) is not list:
                    self.sensors[currentSensor] = []
                    self.sensors.get(currentSensor).append(u)
                else:
                    if not (u in self.sensors.get(currentSensor)):
                        self.sensors.get(currentSensor).append(u)

        if self.robots:
            print "ROBOTS:", self.robots
            print "SENSORS:", self.sensors

        # TODO: Guardar clases?

        self.bigBrother.enter(10, 1, self.update, (self.pyro4ns,))

    def createPyroProxy(self):
        print "Creating proxy for bigBrother"
        try:
            self.daemon = Pyro4.Daemon(host=utils.get_ip_address(ifname=PROXY_INTERFACE), port=PROXY_PORT)
            self.daemon._pyroHmacKey = bytes(PROXY_AND_NS_PASSWORD)
            self.uri = self.daemon.register(self, objectId="bigbrother")
            print "bigBrother running : ", self.uri
            self.daemon.requestLoop()
        except:
            print "Error creando proxy"

    @Pyro4.expose
    def list(self):
        return self.pyro4ns.list()

    @Pyro4.expose
    def lookup(self, name, return_metadata=False):
        _return_metadata = return_metadata
        return self.pyro4ns.lookup(name, return_metadata=_return_metadata)

    @Pyro4.expose
    def ping(self):
        return self.pyro4ns.ping()

    @Pyro4.expose
    def register(self, name, uri, safe=False, metadata=None):
        print "Register", name, uri
        _safe = safe
        _metadata = metadata
        self.pyro4ns.register(name, uri, safe=_safe, metadata=_metadata)

    @Pyro4.expose
    def remove(self, name=None, prefix=None, regex=None):
        _name = name
        _prefix = prefix
        _regex = regex
        self.pyro4ns.remove(name=_name, prefix=_prefix, regex=_regex)

    @Pyro4.expose
    def set_metadata(self, name, metadata):
        return self.pyro4ns.set_metadata(name, metadata)

    @Pyro4.expose
    def proxy(self, name):
        try:
            return Pyro4.Proxy(self.pyro4ns.lookup(name))
        except:
            return None

    # TODO
    @Pyro4.expose
    def request(self, name):
        try:
            return Pyro4.Proxy(self.pyro4ns.lookup(name))
        except:
            return None

    @Pyro4.expose
    def ready(self):
        if self.pyro4ns is not None:
            return True
        else:
            return False


class nameServer(object):
    def __init__(self):
        self.pyro4ns = None  # Nameserver location
        self.ready = False  # Flags
        self.nameserver = None  # Object Name server for Thread-1
        self.nsThread = None  # Thread for NSLoop
        self.start()

    def start(self):
        try:
            self.pyro4ns = Pyro4.locateNS()
            print "NameServer already working"
        except:
            self.nsThread = threading.Thread(
                target=self.createNameServer, args=())
            self.nsThread.start()  # Thread-1 started
            self.pyro4ns = Pyro4.locateNS(hmac_key=bytes(PROXY_AND_NS_PASSWORD))  # Getting NS on main thread

    """Thread-1 loop for nameserver"""
    def createNameServer(self):
        try:
            self.ready = True
            self.nameserver = nm.startNSloop(host="localhost",hmac=bytes(PROXY_AND_NS_PASSWORD))  # NS ready
        except:
            print "Error al crear el nameserver"

    def getPyro4NS(self):
        return self.pyro4ns

    def isWorking(self):
        return self.ready

    ## ------------------------ ADMIN TOOLS -------------------#
    def list(self):
        try:
            print "------------------ NAME-SERVER LIST ------------------"
            print self.pyro4ns.list()
        except:
            print "Error name-server"
            raise

    # TODO
    def listprefix(self, _prefix):
        entries = self.pyro4ns.list(prefix=_prefix)
        return entries

    # TODO
    def listregex(self, _regex):
        entries = self.pyro4ns.list(regex=_regex)
        return entries

    """Get URI for a determinate pyro4object"""

    def lookup(self, name):
        try:
            uri = self.pyro4ns.lookup(name)
            print "Looking for " + name + " : " + colored(uri, "green")
            return uri
        except Pyro4.errors.NamingError:
            print name + " no encontrado."
            name = None

    """Remove a determinate pyro4object"""

    def remove(self, name):
        try:
            print "Removed " + name + " : " + colored(self.pyro4ns.lookup(name), "red")
            self.pyro4ns.remove(name)
        except Pyro4.errors.NamingError:
            print name + " no encontrado."

    """Close nameServer"""

    def exit(self):
        print colored("\nSaliendo...", "red")
        self.nameServerWorking = False
        closer = subprocess.Popen(
            ["sh", "./killer.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        closer.wait()

    """Ctrl+z and Ctrl+c handler"""

    def handler(self, signum, frame):
        self.exit()

    """Return method for string"""

    def execute(self, command):
        return {
            'list': self.list,
            'remove': self.remove,
            'lookup': self.lookup,
            'exit': self.exit,
        }.get(command, None)


if __name__ == "__main__":

    if len(sys.argv) is 2:
        PROXY_INTERFACE = sys.argv[1]
    elif len(sys.argv) is 3:
        PROXY_AND_NS_PASSWORD = sys.argv[1]

    ns_Object = nameServer()
    bb = bigbrother(ns_Object.getPyro4NS())

    signal.signal(signal.SIGTSTP, ns_Object.handler)  # ctrl+z
    signal.signal(signal.SIGINT, ns_Object.handler)  # ctrl+c

    while (True):
        if (ns_Object.isWorking()):  # NS ready for work
            print colored("\n----------\nComandos disponibles: \n* List \n* Remove \n* Lookup\n* Exit\n----------\n", "green")
            command = raw_input(
                "\n" + colored("Comando a la espera: ", "yellow"))
            try:
                command = command.split()
                realCommand = ns_Object.execute(command[0])
                if (realCommand is not None):
                    if (len(command) is 1):
                        realCommand()
                    elif (len(command) is 2):
                        uri = realCommand(command[1])
                        if (uri is not None):
                            proxy = Pyro4.Proxy(uri)
                            # proxy.method()
                            print "URI:", uri, " PROXY: ", proxy
                            print(proxy.get_uris())
                else:
                    print "Comando no encontrado."
            except:
                print(colored("Comando erroneo", "red"))
                raise
        time.sleep(1)
    print printT(color="red"), " saliendo..."
