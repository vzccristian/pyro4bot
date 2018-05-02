import Pyro4
import os
import sys
sys.path.append("../node/libs")
import utils

DEFAULT_BB_PASSWORD = "PyRobot"


class ClientRobot(object):
    """Class to make connections to robots.

    Using a name server and the Pyro4 API, it returns a connection proxy to
    the client in order to work directly with the robot.

    First, distinguish whether you receive a robot name or the connection URI
    directly.

    - If you receive the URI try to make the connection directly.
    If it succeeds, it returns the connections proxy if it returns an error.

    - If it does not receive the URI, but receives the name of the robot, it
     tries to locate a name server in all the network interfaces that it
     has available. If you locate it, check if it is bigbrother or any robot,
     whatever it is, returns the proxy of the robot that was requested.
     If not, returns error.
    """
    def __init__(self, name, port_robot=4041, bigbrother_passw=None):
        """ClientRobot initialization method.

        Args:
            name (str): Name or URI of the robot to be returned.
            port_robot (int): (Optional) Port where the robot works.
            bigbrother_passw (str): Bigbrother's password.
        """
        if ("@" in name):
            self.name = name[0:name.find("@")]
            self.ip = name[name.find("@") + 1:]
            self.ns = False
        else:
            self.name = name
            self.ip = ""
            self.ns = True
        self.port_robot = port_robot
        self.bigbrother_passw = bigbrother_passw if (
            bigbrother_passw) else DEFAULT_BB_PASSWORD
        try:
            proxys = self._proxy_robot()
            Pyro4.config.SERIALIZER = "pickle"
            for p in proxys:
                con = p.split("@")[0].split(".")[1]
                proxy = utils.get_pyro4proxy(p, self.name)
                setattr(self, con, proxy)
        except Exception:
            print("ERROR: conection")
            raise
            exit()

    def _proxy_robot(self):
        proxys = None
        if not self.ns:
            try:
                uri = "PYRO:" + self.name + "@" + \
                    self.ip + ":" + str(self.port_robot)
                self.node = utils.get_pyro4proxy(uri, self.name)
            except Exception:
                print("ERROR: invalid URI: %d" % uri)
                exit()
        else:
            # NameServer o BigBrother
            for x in utils.get_all_ip_address(broadcast=True):
                # print "Locating on :", x
                try:
                    # print "CONFIG",  Pyro4.config.asDict()
                    Pyro4.config.BROADCAST_ADDRS = x
                    ns = Pyro4.locateNS()
                except Exception:
                    ns = None
            if not ns:
                print("ERROR: Unable to locate a name server.")
                exit()
            # BigBrother
            try:
                bb_uri = ns.lookup("bigbrother")
                bb = utils.get_pyro4proxy(bb_uri, self.bigbrother_passw)
                robot_uri = bb.lookup(self.name)
            except Pyro4.errors.NamingError:  # Busco en NS de robot anonimo
                robot_uri = ns.lookup(self.name)
            try:
                self.node = utils.get_pyro4proxy(robot_uri, self.name)
            except Exception:
                self.node = None
        if (self.node):
            try:
                proxys = self.node.get_uris()
                print proxys
            except Exception:
                print("ERROR: Unable to obtain list of robot components: \
                      \n-->[URI]: %s \n-->[NAME]: %s" % (robot_uri, self.name))
                raise
                # os._exit(0)
                # raise
        else:
            print("Robot not found.")
            os._exit(0)
        return proxys
