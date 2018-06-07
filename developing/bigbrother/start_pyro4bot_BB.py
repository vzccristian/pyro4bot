import os
import random
import sched
import signal
import subprocess
import sys
import threading
from threading import *
import time
import Pyro4
import Pyro4.naming as nm
from termcolor import colored
import pprint
import json
import ast
sys.path.append("../node/libs")
import utils
import myjson

DEBUGGER = False


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
        self.mutex = Lock()

        self.private_pyro4ns = _priv_pyro4ns  # Private Pyro4NS location
        self.public_pyro4ns = _pub_pyro4ns  # Public Pyro4NS location

        self.bigBrother = sched.scheduler(time.time, time.sleep)  # bigBrother
        self.bigBrother.enter(5, 1, self.updater, ())  # bigBrother
        self.thread_bigBrother = threading.Thread(
            name="BigBrother",
            target=self.bigBrother.run,
            args=())
        self.thread_bigBrother.setDaemon(1)
        self.thread_bigBrother.start()

        self.thread_proxy = threading.Thread(
            name="Proxy", target=self.create_pyro_proxy, args=())
        self.thread_proxy.setDaemon(1)
        self.thread_proxy.start()

        # Data treatment
        self.robots = {}
        self.components = {}
        self.async_waitings = {}
        self.claimant_list = []

    def updater(self):
        self.update()
        self.bigBrother.enter(10, 1, self.updater, ())

    def update(self, withRemove=True):
        """Update the component dictionary in each robot.

        Go through the list of registered robots and save each of the robots
        in self.components. The key of the dictionary is the component in question
        and the value is a list of all the robots that have this component.
        """
        robots = {x: self.private_pyro4ns.list(
        )[x] for x in self.private_pyro4ns.list() if x not in "Pyro.NameServer"}
        if robots:
            for key, value in robots.iteritems():
                self.robotProxy = Pyro4.Proxy(value)
                self.robotProxy._pyroHmacKey = bytes(key)
                try:
                    robot_uris = self.robotProxy.get_uris()  # Return list uris
                    self.robots[key] = robot_uris
                    for u in robot_uris:
                        currentComponent = u.split(".")[1].split("@")[0]
                        self.components[currentComponent] = []
                        self.components.get(currentComponent).append(u)
                except Exception:
                    if (DEBUGGER):
                        print("Error connecting to: %s " % value)
                    if (withRemove):
                        self.remove(key)

            if (DEBUGGER):
                print "ROBOTS:\n", self.robots
                print "COMPONENTS:\n", self.components
                print "ASYNC_WAITINGS:\n", self.async_waitings
                print "CLAIMANT_LIST:\n", self.claimant_list
        else:
            self.robots = {}
            self.components = {}
            if (DEBUGGER):
                print("There is no registered robot.")

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
            print(colored("\nBigBrother running : {}".format(self.uri), 'green'))
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
    def request(self, obj, claimant):
        if (obj is not None and claimant is not None):
            if (claimant not in self.claimant_list):
                t = threading.Thread(name="t_" + obj + " " + claimant,
                                     target=self.request_loop, args=(obj,))
                self.async_waitings[obj] = {
                    "target_type": -1,
                    "call": t,
                    "claimant": claimant,
                }
                self.claimant_list.append(claimant)
                self.async_waitings[obj]["call"].start()
                if (DEBUGGER):
                    print("REQUEST:\n{}".format(self.async_waitings[obj]))

    def request_loop(self, obj):
        uris = []
        trys = 10
        while((not uris or self.async_waitings[obj]["target_type"] == 3) and self.async_waitings[obj]["claimant"] in self.claimant_list):
            uris, tt = self.lookup(obj, target_type=True, returnAsList=True)
            self.async_waitings[obj]["target_type"] = tt
            time.sleep(5)
        if (DEBUGGER):
            print(colored("\nURI Obtained: {}".format(uris), "green"))
        claimant = self.async_waitings[obj]["claimant"]
        name, comp = claimant.split(".")
        try:
            for robots in self.components.get(comp):
                (name, _, _) = utils.uri_split(robots)
                if (name == self.async_waitings[obj]["claimant"]):
                    while (trys > 0):
                        try:
                            p = utils.get_pyro4proxy(
                                robots, name.split(".")[0])
                            p.add_resolved_remote_dep({obj: uris})
                            break
                        except Exception:
                            trys -= 1
                            time.sleep(3)
                            raise
                break
        except Exception:
            if (DEBUGGER):
                print(
                    colored("\nImposible realizar callback a {}".format(claimant), 'red'))
            else:
                pass

        if claimant in self.claimant_list:
            self.claimant_list.remove(claimant)
        self.async_waitings.pop(obj, None)  # Remove if exists

    @Pyro4.expose
    def lookup(self, obj, return_metadata=False, target_type=False, returnAsList=False):
        if (DEBUGGER):
            print(colored("\nLookup for: {} {}".format(
                obj, return_metadata), "yellow"))
        self.update()
        target_type_info = -1
        uris = []
        try:
            target = obj.split(".")
            if "." in obj:
                # simplebot. o simplebot.*
                if (target[0] and (not target[1] or target[1].count("*") == 1)):
                    target_type_info = 1
                    for x in self.robots[target[0]]:
                        uris.append(x)
                elif target[0] == "?" and target[1]:  # ?.component
                    target_type_info = 2
                    if target[1] in self.components:
                        uris.append(random.choice(self.components[target[1]]))
                elif (target[0].count("*") == 1 and target[1] and
                        target[1].count("*") == 0):  # *.component
                    target_type_info = 3
                    if target[1] in self.components:
                        for x in self.components[target[1]]:
                            uris.append(x)
                elif target[0] and target[1]:  # robot.component
                    target_type_info = 4
                    if target[0] in self.robots:
                        for x in self.robots[target[0]]:
                            if (x[x.find("PYRO:") + 5:x.find("@")] in obj):
                                uris.append(x)
                else:
                    if (DEBUGGER):
                        print "\nInvalid object"
            else:
                target_type_info = 5
                if(returnAsList):
                    for x in self.robots[target[0]]:
                        uris.append(x)
                else:
                    uris.append(self.private_pyro4ns.lookup(obj))
        except Exception:
            print "\nError accesing to:", obj
            return False
        if (target_type):
            return uris, target_type_info
        elif not (returnAsList):
            return uris[0]
        else:
            return uris
        print uris

    @Pyro4.expose
    def ping(self):
        """ Check if nameserver is alive.

        Returns the result of calling the ping () method of nameserver.
        """
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
        if (DEBUGGER):
            print "Registering: ", name, uri, safe, metadata
        _safe = safe
        _metadata = metadata
        self.private_pyro4ns.register(
            name, uri, safe=_safe, metadata=_metadata)
        threading.Thread(name="Updater", target=self.update, args=()).start()

    @Pyro4.expose
    def remove(self, name, prefix=None, regex=None, showInfo=False):
        """Remove robot from nameserver.

        Remove a nameserver robot according to its name
        """
        self.mutex.acquire()
        try:
            if (DEBUGGER or showInfo):
                print "---> Removing:", name, prefix, regex
            _name = name
            _prefix = prefix
            _regex = regex

            if name in self.claimant_list:
                self.claimant_list.remove(name)
            self.private_pyro4ns.remove(
                name=_name, prefix=_prefix, regex=_regex)
            self.update(withRemove=False)
        finally:
            self.mutex.release()

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
        Pyro4.config.SERIALIZERS_ACCEPTED = [
            "json", "marshal", "serpent", "pickle"]

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
            sys.exit(1)
        except Exception:

            self.priv_ns_t = threading.Thread(
                name="Private NameServer",
                target=self.create_nameserver,
                kwargs={'passw': self.config["nameserver_password"]})
            self.priv_ns_t.start()  # Thread-1 started
            time.sleep(1)
            self.private_pyro4ns = Pyro4.locateNS(
                host="localhost",
                hmac_key=bytes(self.config["nameserver_password"]))  # Private NS

            ip = utils.get_ip_address(ifname=self.config["interface"])
            self.pub_ns_t = threading.Thread(
                name="Public NameServer",
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


class adminTool():
    def __init__(self, bigBrother, nameServer):
        self.bigbrother = bigBrother
        self.nameServer = nameServer

    def list(self):
        try:
            print "<-- adminTool -->"
            pprint.pprint(ast.literal_eval(json.dumps(
                self.nameServer.get_priv_pyro4ns().list())))
        except Exception:
            print "Error name-server"
            raise

    def printRobots(self):
        pprint.pprint(ast.literal_eval(json.dumps(self.bigbrother.robots)))

    def printComp(self):
        pprint.pprint(ast.literal_eval(json.dumps(self.bigbrother.components)))

    def printAsync(self):
        print(colored("Components waiting:", "green"))
        pprint.pprint(ast.literal_eval(
            json.dumps(self.bigbrother.claimant_list)))
        print(colored("Components that are needed:", "green"))
        for x in self.bigbrother.async_waitings.keys():
            print("{}. Type: {}. Needed by: {}".format(
                x, self.bigbrother.async_waitings[x]["target_type"], self.bigbrother.async_waitings[x]["claimant"]))

    """Get URI for a determinate pyro4object"""

    def lookup(self, name):
        try:
            uri = self.nameServer.get_priv_pyro4ns().lookup(name)
            print "Looking for " + name + " : " + colored(uri, "green")
            return uri
        except Pyro4.errors.NamingError:
            print name + " no encontrado."
            name = None

    """Remove a determinate pyro4object"""

    def remove(self, name):
        try:
            self.bigbrother.remove(name, showInfo=True)
        except Pyro4.errors.NamingError:
            print name + " no encontrado."
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            print template.format(type(ex).__name__, ex.args)
            time.sleep(2)

    """Close nameServer"""

    def exit(self):
        print colored("\nSaliendo...", "red")
        os._exit(0)

    """Ctrl+z and Ctrl+c handler"""

    def handler(self, signum, frame):
        self.exit()

    def test(self):
        print "<-- adminTool -->"
        pprint.pprint(self.nameServer.__dict__)
        pprint.pprint(self.bigbrother.__dict__)

    def execute(self, command):
        return {
            'robots': self.printRobots,
            'robot': self.printRobots,
            'comp': self.printComp,
            'comps': self.printComp,
            'async': self.printAsync,
            'remove': self.remove,
            'lookup': self.lookup,
            'exit': self.exit,
            'list': self.list,
            'test': self.test,
        }.get(command, None)


if __name__ == "__main__":
    try:
        if len(sys.argv) is 1:
            json_file = load_config("config/bigbrother.json")
        elif len(sys.argv) is 2:
            json_file = load_config(sys.argv[1])
        else:
            print("Only 1 argument is needed <configuration file>.")
            exit(0)

        intfc = colored(json_file["interface"], "yellow")
        print(colored("Starting BigBrother in : {}".format(intfc), 'green'))

        ns_Object = nameServer(json_file)
        bb = bigbrother(ns_Object.get_priv_pyro4ns(),
                        ns_Object.get_pub_pyro4ns(),
                        json_file)
        admintool = adminTool(bb, ns_Object)

        signal.signal(signal.SIGTSTP, admintool.handler)  # ctrl+z
        signal.signal(signal.SIGINT, admintool.handler)  # ctrl+c

        time.sleep(2)
        while (True):
            if (ns_Object.is_working()):  # NS ready for work
                print colored("\n----------\nAvailable commands: " +
                              "\n* robots" +
                              "\n* comps" +
                              "\n* async" +
                              "\n* remove <robot_name>" +
                              "\n* lookup <robot_name>" +
                              "\n* exit" +
                              "\n----------\n", "green")
                command = raw_input(
                    "\n" + colored("Enter a new command: ", "yellow"))
                try:
                    command = command.lower()
                    command = command.split()
                    if (command is not None):
                        realCommand = admintool.execute(command[0])
                        if (len(command) is 1):
                            realCommand()
                        elif (len(command) is 2):
                            uri = realCommand(command[1])
                        elif (len(command) > 2):
                            print(colored("Demasiados argumentos.", "red"))
                    else:
                        print "Comando no encontrado. "
                except Exception:
                    print(colored("Comando erroneo", "red"))
            time.sleep(1)
        print printThread(color="red"), " saliendo..."
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
