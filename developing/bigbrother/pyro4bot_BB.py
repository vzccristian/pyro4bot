import Pyro4
import Pyro4.naming as nm
import utils
from utils import printThread as printT
import sys, threading, time, sched
from termcolor import colored
import signal, subprocess

INTERFACE = "wlan1"


class scheduler(object):
    def __init__(self,object):
        self.scheduler = sched.scheduler(time.time, time.sleep) #Scheduler
        self.robots = None
        self.sensors = None
        print object
        print object.ns
        self.scheduler.enter(5, 1, self.update, (object,)) # Scheduler
        self.tScheduler=threading.Thread(target=self.scheduler.run, args=())
        self.tScheduler.setDaemon(1)
        self.tScheduler.start()

    def update(self,object):
        #TODO
        print printT(), object.ns.list()
        lista = (list(x for x in object.ns.list()))
        print "lista:",lista



        self.scheduler.enter(3, 1, self.update, (object,))

class bigbrother(object):
    def __init__(self, ethernet="wlan1"):
        if (ethernet is not "wlan1"):
            INTERFACE = ethernet
        self.ns = None  # Nameserver location
        self.nameServerWorking = False  # Flags
        self.ready = False  # Flags
        self.nameserver = None  # Name server for Thread-1
        self.nsThread = None  # Thread for NSLoop
        self.start()

    def start(self):
        # Main thread
        print printT(color="yellow"), "--> Checking name_server"
        try:
            # Working
            ns = Pyro4.locateNS()
            print "NameServer already working"
        except:
            # Not working
            self.nameServerWorking = True
            self.nsThread = threading.Thread(
                target=self.createNameServer, args=())
            self.nsThread.start()  # Thread-1 started
            self.ns = Pyro4.locateNS()  # Getting NS on main thread

    """Thread-1 loop for nameserver"""

    def createNameServer(self):
        # Thread-1
        global INTERFACE
        print printT(), "--> Creating new name server on:", colored(INTERFACE, "magenta")
        ip = "localhost"
        while (ip is "localhost"):
            ip = utils.get_ip_address(ifname=INTERFACE)
            if str(ip) is "localhost":
                print "Error al seleccionar interfaz. "
                INTERFACE = raw_input(
                    "\n" + colored("Introducir interfaz de red a utilizar: ", "yellow"))
        try:
            self.ready = True
            self.nameserver = nm.startNSloop(host=ip)  # NS ready
        except:
            print "Error al crear el nameserver"

    """Get URI list"""
    def list(self):
        try:
            print "------------------ NAME-SERVER LIST ------------------"
            print self.ns.list()
        except:
            print "Error name-server"
            raise

    # TODO
    def listprefix(self, _prefix):
        entries = self.ns.list(prefix=_prefix)
        return entries

    # TODO
    def listregex(self, _regex):
        entries = self.ns.list(regex=_regex)
        return entries

    """Get URI for a determinate pyro4object"""
    def lookup(self, name):
        try:
            uri = self.ns.lookup(name)
            print "Looking for " + name + " : " + colored(uri, "green")
            return uri
        except Pyro4.errors.NamingError:
            print name + " no encontrado."
            name = None


    """Remove a determinate pyro4object"""
    def remove(self, name):
        try:
            print "Removed " + name + " : " + colored(self.ns.lookup(name), "red")
            self.ns.remove(name)
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
    threading.current_thread().setName("Main")
    if len(sys.argv) > 1:
        INTERFACE = sys.argv[1]
    bb = bigbrother(ethernet=INTERFACE)
    sch = scheduler(bb)

    signal.signal(signal.SIGTSTP, bb.handler)  # ctrl+z
    signal.signal(signal.SIGINT, bb.handler)  # ctrl+c

    # Main thread
    while (bb.nameServerWorking):
        time.sleep(1)
        if (bb.ready):
            print colored("----------------------\nComandos disponibles: \n* List \n* Remove \n* Lookup\n* Exit\n----------------------", "green")
            command = raw_input(
                "\n" + colored("Comando a la espera: ", "yellow"))
            try:
                command=command.split()
                realCommand = bb.execute(command[0])
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
                raise
                print (colored("Comando erroneo", "red"))

    print printT(color="red"), " saliendo..."
