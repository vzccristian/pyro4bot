import os
import random
import sched
import signal
import subprocess
import sys
import threading
import time

import Pyro4
import Pyro4.naming as nm
from termcolor import colored

sys.path.append("../node/libs")
import utils
import myjson


def load_config(filename):
    return myjson.MyJson(filename).json


class bigbrother(object):
    """BigBrothers controls communications middleware.

    Bigbrother is responsible for allowing or not accessing the name server.
    """

    def __init__(self, _priv_pyro4ns, _pub_pyro4ns, config):
        """__init__ method of BigBrother.

        Args:
            _priv_pyro4ns (nameServer): private nameServer object from
                custom class nameServer
            _pub_pyro4ns (nameServer): public nameServer object from
                custom class nameServer
            config : dict obtaneid from json file
        """
        self.config = config

        self.private_pyro4ns = _priv_pyro4ns  # Private Pyro4NS location
        self.public_pyro4ns = _pub_pyro4ns  # Public Pyro4NS location

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
        robots = {x: self.private_pyro4ns.list(
        )[x] for x in self.private_pyro4ns.list() if x not in "Pyro.NameServer"}

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
        json file.
        Obtain a connection port from the port indicated in json file.

        Next, it creates a daemon that is the connection proxy
        to BigBrother and registers itself.

        It is working in the background listening to requests.
        """
        try:
            myip = utils.get_ip_address(ifname=self.config["interface"])
            myport = utils.get_free_port(self.config["proxy_port"], ip=myip)

            daemon = Pyro4.Daemon(host=myip, port=myport)
            daemon._pyroHmacKey = bytes(self.config["proxy_password"])

            daemon.PYRO_MAXCONNECTIONS = 20

            self.uri = daemon.register(self, objectId="bigbrother")
            print "\nBigBrother running :", self.uri
            self.public_pyro4ns.register("bigbrother", self.uri)
            daemon.requestLoop()
        except Exception:
            print "Error creating proxy on interface", self.config["interface"]
            raise

    @Pyro4.expose
    def list(self):
        """List all objects registered in nameserver.

        Returns a dictionary where the key is the name of the object
        and the value is the URI associated with that object
        """
        return self.private_pyro4ns.list()

    @Pyro4.expose
    def lookup(self, obj, return_metadata=False, async=False):
        """Look up a single name registration and return the uri.

        Returns the URI associated with the last name as argument.

        Args:
            name (str): Object name
            return_metadata (boolean, optional) : By default it is False,
                and you just get back the registered URI (lookup).
                If you set it to True, you will get back tuples instead:
                (uri, set-of-metadata-tags):
        """
        # print "Lookup:", obj, return_metadata, async
        _return_metadata = return_metadata
        self.update()
        uris = []
        try:
            target = obj.split(".")
            if "." in obj:
                if (target[0] and (not target[1] or target[1].count("*") == 1)):  # simplebot. o simplebot.*
                    # print("#1")
                    for x in self.robots[target[0]]:
                        uris.append(x)
                elif target[0] == "?" and target[1]:  # ?.sensor
                    # print("#2")
                    if target[1] in self.sensors:
                        uris.append(random.choice(self.sensors[target[1]]))
                elif (target[0].count("*") == 1 and target[1] and
                        target[1].count("*") == 0):  # *.sensor
                    # print("#3")
                    if target[1] in self.sensors:
                        for x in self.sensors[target[1]]:
                            uris.append(x)
                elif target[0] and target[1]:
                    # print("#4")
                    if target[0] in self.robots:
                        return [x for x in self.robots[target[0]] if (target[1] in x)]
                else:
                    print "Objeto no valido"
            else:
                for x in self.robots[target[0]]:
                    uris.append(x)
        except Exception:
            print "Error al acceder a", obj
            return False
        return uris

    @Pyro4.expose
    def ping(self):
        """ Check if nameserver is alive.

        Returns the result of calling the ping () method of nameserver.
        """
        print "Pinging..."
        return self.private_pyro4ns.ping()

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
        self.private_pyro4ns.register(name, uri, safe=_safe, metadata=_metadata)
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

        self.sensors = {key: list_sensors for key, list_sensors in self.sensors.items() for s in list_sensors if s in self.robots[name]}
        self.robots.pop(name, None)

        self.private_pyro4ns.remove(name=_name, prefix=_prefix, regex=_regex)
        threading.Thread(target=self.update, args=()).start()

    @Pyro4.expose
    def set_metadata(self, name, metadata):
        return self.private_pyro4ns.set_metadata(name, metadata)

    @Pyro4.expose
    def proxy(self, obj, passw=None):
        all_proxys = []
        for x in self.lookup(obj):
            if (passw is None):
                passw = obj.split(".")[0]
            all_proxys.append(utils.get_pyro4proxy(x, passw))
        return all_proxys

    @Pyro4.expose
    def ready(self):
        if self.private_pyro4ns is not None:
            return True
        else:
            return False


class nameServer(object):
    def __init__(self, config):
        self.config = config
        Pyro4.config.SERIALIZERS_ACCEPTED = ["json", "marshal", "serpent", "pickle"]
        # Public NS
        self.public_pyro4ns = None  # Public Nameserver location
        self.pub_nameserver = None  # Object Name server for Thread-1
        self.pub_ns_t = None  # Thread for NSLoop

        # Private NS
        self.private_pyro4ns = None  # Nameserver location
        self.priv_ready = False  # Flags
        self.priv_nameserver = None  # Object Name server for Thread-1
        self.priv_ns_t = None  # Thread for NSLoop

        self.start()

    def start(self):
        try:
            self.private_pyro4ns = Pyro4.locateNS()
            print "NameServer already working"
        except Exception:
            self.priv_ns_t = threading.Thread(
                target=self.create_nameserver,
                kwargs={'passw': self.config["nameserver_password"]})
            self.priv_ns_t.start()  # Thread-1 started
            time.sleep(1)
            self.private_pyro4ns = Pyro4.locateNS(
                host="localhost",
                hmac_key=bytes(self.config["nameserver_password"]))  # Private NS

            ip = utils.get_ip_address(ifname=self.config["interface"])
            self.pub_ns_t = threading.Thread(
                target=self.create_nameserver,
                kwargs={'host': ip, })
            self.pub_ns_t.start()
            time.sleep(1)
            self.public_pyro4ns = Pyro4.locateNS(host=ip)  # Public NS

    """Thread-1 loop for nameserver"""

    def create_nameserver(self, host="localhost", passw=False):
        try:
            if ("localhost" in host):  # Private NS
                self.priv_ready = True
                print(colored("Started private name server.", 'yellow'))
                self.priv_nameserver = nm.startNSloop(
                    host=host, hmac=bytes(passw))
            else:  # Public NS
                print(colored("Started public name server.", 'yellow'))
                self.pub_nameserver = nm.startNSloop(host=host)
        except Exception:
            print("Error al crear el nameserver %s" % host)

    def get_priv_pyro4ns(self):
        return self.private_pyro4ns

    def get_pub_pyro4ns(self):
        return self.public_pyro4ns

    def is_working(self):
        return self.priv_ready

    # ------------------------ ADMIN TOOLS -------------------#
    def list(self):
        try:
            print "------------------ NAME-SERVER LIST ------------------"
            print self.private_pyro4ns.list()
        except Exception:
            print "Error name-server"
            raise

    # TODO
    def listprefix(self, _prefix):
        entries = self.private_pyro4ns.list(prefix=_prefix)
        return entries

    # TODO
    def listregex(self, _regex):
        entries = self.private_pyro4ns.list(regex=_regex)
        return entries

    """Get URI for a determinate pyro4object"""

    def lookup(self, name):
        try:
            uri = self.private_pyro4ns.lookup(name)
            print "Looking for " + name + " : " + colored(uri, "green")
            return uri
        except Pyro4.errors.NamingError:
            print name + " no encontrado."
            name = None

    """Remove a determinate pyro4object"""

    def remove(self, name):
        try:
            print("Removed " + name + " : " +
                  colored(self.private_pyro4ns.lookup(name), "red"))
            self.private_pyro4ns.remove(name)
        except Pyro4.errors.NamingError:
            print name + " no encontrado."

    """Close nameServer"""

    def exit(self):
        print colored("\nSaliendo...", "red")
        self.priv_nameserverWorking = False
        closer = subprocess.Popen(
            ["sh", "./killer.sh"], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        closer.wait()
        os._exit(0)

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
    try:
        if len(sys.argv) is 1:
            json_file = load_config("config/bigbrother.json")
        elif len(sys.argv) is 2:
            json_file = load_config(sys.argv[1])
        else:
            print "Demasiados argumentos."
            exit(0)

        print(colored("Starting BigBrother...", 'green'))

        ns_Object = nameServer(json_file)
        bb = bigbrother(ns_Object.get_priv_pyro4ns(),
                        ns_Object.get_pub_pyro4ns(),
                        json_file)

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
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
