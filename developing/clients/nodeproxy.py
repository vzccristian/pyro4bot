import Pyro4
import os
import sys
sys.path.append("../node/libs")
import utils

class ClientNODERB(object):
    def __init__(self, name, port_robot=4041, ns=True):
        if ("@" in name):
            self.name = name[0:name.find("@")]
            self.ip = name[name.find("@") + 1:]
            self.ns = False
            print name
        else:
            self.name = name
            self.ip = ""
            self.ns = True
            print name
        self.port_robot = port_robot
        try:
            self.proxy_robot()
            Pyro4.config.SERIALIZER = "pickle"
            for p in self.proxys:
                con = p.split("@")[0].split(".")[1]
                proxy = Pyro4.Proxy(p)
                proxy._pyroHmacKey = bytes(self.name)
                setattr(self, con, proxy)
        except Exception:
            print("ERROR: conection")
            raise
            exit()

    def proxy_robot(self):
        self.proxys = None
        if not self.ns:
            try:
                uri = "PYRO:" + self.name + "@" + self.ip + ":" + str(self.port_robot)
                self.node = Pyro4.Proxy(uri)
            except Exception:
                print("ERROR: invalid URI: %d" % uri)
                exit()
        else:
            # NameServer o BigBrother
            for x in utils.get_all_ip_address():
                print "Locating on :", x
                try:
                    # TODO
                    # Pyro4.config.NS_HOST = Pyro4.config.NS_BCHOST = x
                    # print "CONFIG",  Pyro4.config.NS_HOST
                    # print Pyro4.config.NS_PORT
                    # print Pyro4.config.HOST
                    # print Pyro4.config.NS_BCHOST
                    # print Pyro4.config.NS_BCPORT
                    ns = Pyro4.locateNS()
                except Exception:
                    ns = None
            if not ns:
                print "No se puede localizar un servidor de nombres."
                exit()
            # BigBrother
            try:
                bb_uri = ns.lookup("bigbrother")
                bb = Pyro4.Proxy(bb_uri)
                bb._pyroHmacKey = bytes("PyRobot")
                robot_uri = bb.lookup(self.name)
            except Pyro4.errors.NamingError:  # Busco en NS de robot
                robot_uri = ns.lookup(self.name)
            try:
                self.node = Pyro4.Proxy(robot_uri)
                self.node._pyroHmacKey = bytes(self.name)
            except Exception:
                self.node = None
        if (self.node):
            self.proxys = self.node.get_uris()
            print self.proxys
        else:
            print "Robot no encontrado"
            os._exit(0)
        return self.proxys
