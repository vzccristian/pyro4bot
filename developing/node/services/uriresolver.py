


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lock().acquire()
#____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control, utils
import Pyro4
from termcolor import colored

PASSWORD = "PyRobot"

@Pyro4.expose
class uriresolver(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        Pyro4.config.HOST = self.ip
        self.URIS = {}
        # print self.pyro4id
        self.ns = None
        self.get_ns()
        super(uriresolver, self).__init__()

    def get_ns(self):
        try:
            # self.ns = Pyro4.locateNS()  # hay que pasar el port y no funciona
            if self.ns is None:
                print "Obteniendo... Proxy de BigBrother en self.ns"
                self.ns = Pyro4.Proxy("PYRO:bigbrother@192.168.10.1:6060")
                self.ns._pyroHmacKey = bytes(PASSWORD)
        except:
            print "Error al conectar a BigBrother"
            return False
        return self.ns.ready()

    def ready(self):
        print "ready en uriresolver"
        return self.ns.ready()

    def new_uri(self, name, mode="public"):
        if mode == "local":
            ip = "127.0.0.1"
        else:
            ip = self.ip
        port_node = self.port_node
        start_port = self.start_port
        while not utils.free_port(port_node, ip):
            port_node += 10
        while not utils.free_port(start_port, ip):
            start_port += 1
        if name.find(self.basename) > -1:
            if name != self.basename:
                uri = "PYRO:" + name + "@" + ip + ":" + str(start_port)
            else:
                uri = "PYRO:" + name + "@" + ip + ":" + str(port_node)
        else:
            print("resolver por dns")
            uri = "PYRO:" + name + "@" + self.ip + ":" + str(start_port)
        #print ("uri resolved: %s" %(uri))
        self.URIS[name] = uri
        self.start_port = start_port + 1
        self.port_node = port_node + 1
        return uri

    def split(self, uri):
        name = uri[uri.find("PYRO:") + 5:uri.find("@")]
        ip = uri[uri.find("@") + 1:uri.find(":", 7)]
        port = int(uri[uri.find(":", 7) + 1:])
        return list(name, ip, port)

    def get_uri(self, name):
        if self.URIS.has_key(name):
            return self.URIS[name]
        else:
            return None

    def get_name(self, uri):
        for k, v in self.URIS.iteritems():
            if v == uri:
                return k
        return None

    def wait_available(self, uri, trys=20):  # eso puede ser asinc return
        conect = False
        if uri.find("@") == -1:
            uri = self.get_uri(uri)
        try:
            p = Pyro4.Proxy(uri)
        except:
            return None
        while not conect and trys > 0:
            trys = trys - 1
            try:
                conect = p.echo() == "hello"
            except:
                conect = False
            time.sleep(0.2)
        if conect:
            return uri
        else:
            return None

    def wait_resolv_remotes(self, name, trys=10):
        conect = False
        if not self.ns:
            return None
        while not conect and trys > -1:
            try:
                getbot = self.ns.lookup(name[0:name.find(".")])
                proxy = Pyro4.Proxy(getbot)
                remoteuri, status = proxy.get_name_uri(name)
                conect = (remoteuri != None and status not in ["down", "wait"])
            except:
                # print "error remote"
                pass
            trys -= 1
            time.sleep(0.05)
        if trys < 0:
            return name
        if conect:
            return remoteuri

    def register_robot(self, uri):
        print "register_robot"
        #./print(self.basename,self.URIS[self.basename])
        # self.ns.register(self.basename, self.URIS[self.basename])
        try:
            if self.ns != False:

                # print "___________REGISTERING PYRO4BOT ON NAME SERVER_________________"
                self.URIS[self.basename] = uri

                self.ns.register(self.basename, self.URIS[self.basename])
                print("REGISTERING NAME SERVER URI: %s" %
                      (colored(self.URIS[self.basename], 'green')))
            else:
                print(colored("NAME SERVER NOT FIND", 'red'))

        except:
            print("ERROR:name server not find")
            raise

    def list_uris(self, node=False):
        if node:
            return [self.URIS[x] for x in self.URIS]
        else:
            return [self.URIS[x] for x in self.URIS if x.find(".") > -1]


if __name__ == "__main__":
    pass
