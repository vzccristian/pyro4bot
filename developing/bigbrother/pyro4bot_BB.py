import Pyro4
import Pyro4.naming as nm
import utils
from utils import printThread as printT
import sys, threading, time, sched
from termcolor import colored
import signal, subprocess
import rpc_server

INTERFACE = "wlan1"
PASSWORD = "PyRobot"
PORT = 17000


""" Class for NS gestion """
class bigbrother(object):
    def __init__(self,_pyro4ns):
        self.pyro4ns = _pyro4ns #Pyro4NS location

        self.bigBrother = sched.scheduler(time.time, time.sleep) #bigBrother
        self.bigBrother.enter(5, 1, self.update, (self.pyro4ns ,)) # bigBrother
        self.thread_bigBrother=threading.Thread(target=self.bigBrother.run, args=())
        self.thread_bigBrother.setDaemon(1)
        self.thread_bigBrother.start()

        self.thread_rpc_server=threading.Thread(target=self.createRPCServer, args=())
        self.thread_rpc_server.setDaemon(1)
        self.thread_rpc_server.start()

        #Data treatment
        self.robots = {}
        self.sensors = {}

    """ TODO """
    def update(self,pyro4ns):
        self.robots = {x: self.pyro4ns.list()[x] for x in self.pyro4ns.list() if x not in "Pyro.NameServer"}
        self.bigBrother.enter(20, 1, self.update, (self.pyro4ns ,))

    """Create RPC server"""
    def createRPCServer(self):
        rcp = rpc_server.RPCHandler()
        # Interface methods
        rcp.register_function(self.list)
        rcp.register_function(self.lookup)
        rcp.register_function(self.ping)
        rcp.register_function(self.register)
        rcp.register_function(self.remove)
        rcp.register_function(self.set_metadata)
        rcp.register_function(self.proxy)
        rpc_server.rpc_server(rcp, ('localhost', PORT), authkey=bytes(PASSWORD))

    #TODO: Add decorator for all interface methods?
    
    def list(self):
        return self.pyro4ns.list()

    def lookup(self,name,return_metadata=False):
        _return_metadata = return_metadata
        return self.pyro4ns.lookup(name,return_metadata=_return_metadata)

    def ping(self):
        return self.pyro4ns.ping()

    def register(self,name, uri, safe=False, metadata=None):
        _safe = safe
        _metadata = metadata
        self.pyro4ns.register(name,uri,safe=_safe,metadata=_metadata)

    def remove(self,name=None, prefix=None, regex=None):
        _name = name
        _prefix = prefix
        _regex = regex
        self.pyro4ns.remove(name=_name,prefix=_prefix,regex=_regex)

    def set_metadata(self,name, metadata):
        return self.pyro4ns.set_metadata(name,metadata)

    """Pyro4 proxy"""
    def proxy(self,name):
        try:
            # print (self.pyro4ns.lookup(name))
            return Pyro4.Proxy(self.pyro4ns.lookup(name))
        except:
            return None

class nameServer(object):
    def __init__(self):
        self.pyro4ns = None  # Nameserver location

        self.ready = False  # Flags

        self.nameserver = None  # Object Name server for Thread-1
        self.nsThread = None  # Thread for NSLoop
        self.start()

    def start(self):
        print printT(color="yellow"), "--> Checking name_server"
        try:
            self.pyro4ns = Pyro4.locateNS()
            print "NameServer already working"
        except:
            self.nsThread = threading.Thread(target=self.createNameServer, args=())
            self.nsThread.start()  # Thread-1 started
            self.pyro4ns = Pyro4.locateNS()  # Getting NS on main thread

    """Thread-1 loop for nameserver"""

    def createNameServer(self):
        global INTERFACE
        print printT(), "--> Creating new name server on:", colored(INTERFACE, "magenta")
        ip = "localhost"
        while (ip is "localhost"):
            ip = utils.get_ip_address(ifname=INTERFACE)
            if str(ip) is "localhost":
                print "Error al seleccionar interfaz. "
                INTERFACE = raw_input("\n" + colored("Introducir interfaz de red a utilizar: ", "yellow"))
        try:
            self.ready = True
            self.nameserver = nm.startNSloop(host=ip)  # NS ready
        except:
            print "Error al crear el nameserver"

    def getPyro4NS(self):
        return self.pyro4ns

    def isWorking(self):
        return self.ready

    ## ------------------------ ADMIN TOOLS -------------------#
    """Get URI list"""
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
    threading.current_thread().setName("Main")
    if len(sys.argv) is 2:
        INTERFACE = sys.argv[1]
    elif len(sys.argv) is 3:
        PASSWORD = sys.argv[1]

    ns_Object = nameServer()
    bb = bigbrother(ns_Object.getPyro4NS())

    signal.signal(signal.SIGTSTP, ns_Object.handler)  # ctrl+z
    signal.signal(signal.SIGINT, ns_Object.handler)  # ctrl+c

    # Main thread
    while (True):
        if (ns_Object.isWorking()): #NS ready for work
            print colored("\n----------------------\nComandos disponibles: \n* List \n* Remove \n* Lookup\n* Exit\n----------------------", "green")
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
                print (colored("Comando erroneo", "red"))
                raise
        time.sleep(1)
    print printT(color="red"), " saliendo..."
