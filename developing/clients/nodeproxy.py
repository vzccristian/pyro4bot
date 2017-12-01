import Pyro4


class ClientNODERB(object):
    def __init__(self, name, port_robot=4040, ns=True):
        if name.find("@") > -1:
            self.name = name[0:name.find("@")]
            self.ip = name[name.find("@") + 1:]
            self.ns = False
        else:
            self.name = name
            self.ip = ""
            self.ns = True
        self.port_robot = port_robot
        # self.ns=ns
        try:
            self.proxy_robot()
            # print self.proxys
            Pyro4.config.SERIALIZER = "pickle"
            #Pyro4.config.SERIALIZERS_ACCEPTED=set(['pickle','json', 'marshal', 'serpent'])
            for p in self.proxys:
                con = p.split("@")[0].split(".")[1]
                setattr(self, con, Pyro4.Proxy(p))
        except:
            print("ERROR: conection")
            raise
            exit()

    def proxy_robot(self):
        try:
            self.proxys = []
            if self.ns != True:
                self.node = Pyro4.Proxy(
                    "PYRO:" + self.name + "@" + self.ip + ":" + str(self.port_robot))

            else:
                self.node = Pyro4.Proxy("PYRONAME:" + self.name)
            self.proxys = self.node.get_uris()
            return self.proxys
        except:
            print("ERROR: conection")
            raise
            exit()
