import Pyro4
import Pyro4.naming as nm
import sys
import threading
import time
import sched
from termcolor import colored
import signal
import subprocess
import os
os.path.abspath('../node/libs')
import utils
os.path.abspath('.')

PROXY_AND_NS_PASSWORD = "PyRobot"
PROXY_PORT = 6060
PROXY_INTERFACE = "wlan1"


class bigbrother(object):
    """BigBrothers controls communications middleware.

    Bigbrother is responsible for allowing or not accessing the name server.
    """

    def __init__(self, _pyro4ns):
        """__init__ method of BigBrother.

        Args:
            _pyro4ns (nameServer): nameServer object from
                custom class nameServer
        """
        self.pyro4ns = _pyro4ns  # Pyro4NS location

        self.bigBrother = sched.scheduler(time.time, time.sleep)  # bigBrother
        self.bigBrother.enter(5, 1, self.updater, ())  # bigBrother
        self.thread_bigBrother = threading.Thread(
            target=self.bigBrother.run, args=())
        self.thread_bigBrother.setDaemon(1)
        self.thread_bigBrother.start()

        self.thread_proxy = threading.Thread(
            target=self.create_pyro_proxy, args=())
        self.thread_proxy.setDaemon(1)
        self.thread_proxy.start()

        # Data treatment
        self.robots = {}
        self.sensors = {}

    def updater(self):
        self.update()
        self.bigBrother.enter(10, 1, self.updater, ())

    def update(self):
        """Update the sensor dictionary in each robot.

        Go through the list of registered robots and save each of the robots
        in self.sensors. The key of the dictionary is the sensor in question
        and the value is a list of all the robots that have this sensor.
        """
        robots = {x: self.pyro4ns.list(
        )[x] for x in self.pyro4ns.list() if x not in "Pyro.NameServer"}

        for key, value in robots.iteritems():
            self.robotProxy = Pyro4.Proxy(value)
            self.robotProxy._pyroHmacKey = bytes(key)
            try:
                robot_uris = self.robotProxy.get_uris()  # Return list uris
                self.robots[key] = robot_uris
                for u in robot_uris:
                    currentSensor = u.split(".")[1].split("@")[0]
                    if type(self.sensors.get(currentSensor)) is not list:
                        self.sensors[currentSensor] = []
                        self.sensors.get(currentSensor).append(u)
                    else:
                        if not (u in self.sensors.get(currentSensor)):
                            self.sensors.get(currentSensor).append(u)
            except Exception:
                print("Error connecting to: %s " % value)
                self.remove(key)
        if self.robots:
            print "ROBOTS:", self.robots
            print "SENSORS:", self.sensors

    def create_pyro_proxy(self):
        """Create proxy to make connections to BigBrother.

        Gets the network address of the network interface indicated in
        the global variable PROXY_INTERFACE.
        Obtain a connection port from the port indicated in PROXY_PORT.

        Next, it creates a daemon that is the connection proxy
        to BigBrother and registers itself.

        It is working in the background listening to requests.
        """
        try:
            myip = utils.get_ip_address(ifname=PROXY_INTERFACE)
            myport = utils.get_free_port(PROXY_PORT, ip=myip)

            daemon = Pyro4.Daemon(host=myip, port=myport)
            daemon._pyroHmacKey = bytes(PROXY_AND_NS_PASSWORD)

            daemon.PYRO_MAXCONNECTIONS = 20

            self.uri = daemon.register(self, objectId="bigbrother")
            print "\nBigBrother running : ", self.uri
            daemon.requestLoop()
        except Exception:
            print "Error creating proxy on interface", PROXY_INTERFACE

    @Pyro4.expose
    def list(self):
        """List all objects registered in nameserver.

        Returns a dictionary where the key is the name of the object
        and the value is the URI associated with that object
        """
        return self.pyro4ns.list()

    @Pyro4.expose
    def lookup(self, name, return_metadata=False):
        """Look up a single name registration and return the uri.

        Returns the URI associated with the last name as argument.

        Args:
            name (str): Object name
            return_metadata (boolean, optional) : By default it is False,
                and you just get back the registered URI (lookup).
                If you set it to True, you will get back tuples instead:
                (uri, set-of-metadata-tags):
        """
        print "Lookup:", name, return_metadata
        _return_metadata = return_metadata
        return self.pyro4ns.lookup(name, return_metadata=_return_metadata)

    @Pyro4.expose
    def ping(self):
        """ Check if nameserver is alive.

        Returns the result of calling the ping () method of nameserver.
        """
        print "Pinging..."
        return self.pyro4ns.ping()

    @Pyro4.expose
    def register(self, name, uri, safe=False, metadata=None):
        """Register new robot on nameserver.

        Registra un nuevo robot en nameserver haciendo uso del metodo
        register() de Pyro4.naming

        Args:
            name (str): Object name to register
            uri (str): URI associated with the name of the object
            safe (bool): normally registering the same name twice silently
                overwrites the old registration.
                If you set safe=True, the same name cannot be registered twice.
        """
        print "Registering: ", name, uri, safe, metadata
        _safe = safe
        _metadata = metadata
        self.pyro4ns.register(name, uri, safe=_safe, metadata=_metadata)
        threading.Thread(target=self.update, args=()).start()

    @Pyro4.expose
    def remove(self, name, prefix=None, regex=None):
        """Remove robot from nameserver.

        Remove a nameserver robot according to its name
        """
        print "Removing:", name, prefix, regex
        _name = name
        _prefix = prefix
        _regex = regex
        for uri in self.robots:
            uri = self.robots[name]
            self.sensors = {key: value for key, value in self.sensors.items()
                            if value != uri}
        del self.robots[name]

        self.pyro4ns.remove(name=_name, prefix=_prefix, regex=_regex)
        threading.Thread(target=self.update, args=()).start()

    @Pyro4.expose
    def set_metadata(self, name, metadata):
        return self.pyro4ns.set_metadata(name, metadata)

    @Pyro4.expose
    def proxy(self, obj, passw=None):
        target = obj.split(".")
        try:
            all_proxys = []
            if (target[0] and (not target[1] or target[1].count("*") == 1)):  # simplebot. o simplebot.*
                for x in self.robots[target[0]].iteritems():
                    all_proxys.append(utils.get_pyro4proxy(x, target[0]))
                return all_proxys
            elif (not target[0] and target[1]):  # .sensor
                for x in self.sensors[target[1]].iteritems():
                    return utils.get_pyro4proxy(x, target[0])
            elif (target[0].count("*") == 1 and target[1] and
                    target[1].count("*") == 0):  # *.sensor
                for x in self.sensors[target[1]].iteritems():
                    all_proxys.append(utils.get_pyro4proxy(x, target[0]))
                return all_proxys
            elif (target[0].count("*") == 1 and target[0].count("*")):
                print target, "obj7" # TODO regex
            else:
                print "Objeto no valido"
        except Exception:
            print "Error al acceder a", target

        # try:
        #     if ('@' in obj):
        #         (name, ip, port) = utils.uri_split(obj)
        #         proxy = Pyro4.Proxy(name)
        #         if not (passw):
        #             passw = name
        #     else:
        #         proxy = Pyro4.Proxy(self.pyro4ns.lookup(obj))
        #         if not (passw):
        #             passw = obj
        #     proxy._pyroHmacKey = bytes(passw)
        #     return proxy
        # except Exception:
        #     return None

    # TODO
    @Pyro4.expose
    def request(self, name):
        try:
            return Pyro4.Proxy(self.pyro4ns.lookup(name))
        except Exception:
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
        except Exception:
            self.nsThread = threading.Thread(
                target=self.create_nameserver, args=())
            self.nsThread.start()  # Thread-1 started
            self.pyro4ns = Pyro4.locateNS(hmac_key=bytes(
                PROXY_AND_NS_PASSWORD))  # Getting NS on main thread

    """Thread-1 loop for nameserver"""

    def create_nameserver(self):
        try:
            self.ready = True
            self.nameserver = nm.startNSloop(
                host="localhost", hmac=bytes(PROXY_AND_NS_PASSWORD))
            # NS ready
        except Exception:
            print "Error al crear el nameserver"

    def get_pyro4ns(self):
        return self.pyro4ns

    def is_working(self):
        return self.ready

    # ------------------------ ADMIN TOOLS -------------------#
    def list(self):
        try:
            print "------------------ NAME-SERVER LIST ------------------"
            print self.pyro4ns.list()
        except Exception:
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
            print("Removed " + name + " : " +
                  colored(self.pyro4ns.lookup(name), "red"))
            self.pyro4ns.remove(name)
        except Pyro4.errors.NamingError:
            print name + " no encontrado."

    """Close nameServer"""

    def exit(self):
        print colored("\nSaliendo...", "red")
        self.nameServerWorking = False
        closer = subprocess.Popen(
            ["sh", "./killer.sh"], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
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
    bb = bigbrother(ns_Object.get_pyro4ns())

    signal.signal(signal.SIGTSTP, ns_Object.handler)  # ctrl+z
    signal.signal(signal.SIGINT, ns_Object.handler)  # ctrl+c

    while (True):
        if (ns_Object.is_working()):  # NS ready for work
            print colored("\n----------\nComandos disponibles: \n* List \n* Remove \n* Lookup\n* Exit\n----------\n", "green")
            command = raw_input(
                "\n" + colored("Comando a la espera: ", "yellow"))
            try:
                command = command.split()
                if (command is not None):
                    realCommand = ns_Object.execute(command[0])
                    if (len(command) is 1):
                        realCommand()
                    elif (len(command) is 2):
                        uri = realCommand(command[1])
                        if (uri is not None):
                            proxy = Pyro4.Proxy(uri)
                            # proxy.method()
                            print "URI:", uri, " PROXY: ", proxy
                            print(proxy.get_uris())
                    elif (len(command) > 2):
                        print(colored("Demasiados argumentos.", "red"))
                else:
                    print "Comando no encontrado."
            except Exception:
                print(colored("Comando erroneo", "red"))
        time.sleep(1)
    print printThread(color="red"), " saliendo..."
