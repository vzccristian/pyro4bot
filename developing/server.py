# saved as greeting-server.py
import Pyro4

def methods(ob):
    return [method for method in dir(ob) if callable(getattr(ob, method)) and method[0]!="_"]

def create_hooks(clas,obj,obj_name):
    obj_n=obj.__class__.__name__
    for m in methods(obj):
      setattr(clas, obj_name+"_"+m, getattr(obj,m))
      print("hooking "+obj_name+"."+m)

@Pyro4.expose
class calculator(object):
    def suma(self,a,b):
        self.pp="DDD"
        return a+b
@Pyro4.expose
class texto(object):
    def eco(self,p):
        print(p)
        return p
@Pyro4.expose
class server(object):
    def __init__(self):
        self.cal=calculator()
        self.text=texto()
        create_hooks(server,self.cal,"cal")
        create_hooks(server,self.text,"text")
        print methods(self)

    def hello(self, name):
        return "Hello, %s" % name

if __name__ == "__main__":
    Pyro4.config.HOST="192.168.1.35"
    daemon = Pyro4.Daemon()                # make a Pyro daemon
    ns = Pyro4.locateNS()
    ser=server()
    uri = daemon.register(ser)
    print uri
    ns.register("example.server", uri)   # register the object with a name in the name server
    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls
