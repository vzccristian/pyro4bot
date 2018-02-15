import Pyro4
import os

class ClientNODERB(object):
    def __init__(self, name, port_robot=4041, ns=True):
        if ("@" in name):
            self.name = name[0:name.find("@")]
            self.ip = name[name.find("@") + 1:]
            self.ns = False
        else:
            self.name = name
            self.ip = ""
            self.ns = True
        self.port_robot = port_robot
        self.proxy_robot()
        try:
            Pyro4.config.SERIALIZER = "pickle"
            for p in self.proxys:
                con = p.split("@")[0].split(".")[1]
                proxy = Pyro4.Proxy(p)
                proxy._pyroHmacKey = bytes(self.name)
                setattr(self, con, proxy)
        except Exception:
            print("ERROR: conection")
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
            try:
                ns = Pyro4.locateNS(host="192.168.10.1")
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
                    self.proxys = self.node.get_uris()
                except Exception:
                    self.node = None
                    print "Robot no encontrado"
                    os._exit(0)
            except Exception:
                print "No se puede localizar un servidor de nombres."
        return self.proxys
