import time
import threading
import Pyro4
import utils


# decoradores para las clases generales
def load_config(in_function):
    def out_function(*args, **kwargs):
        _self = args[0]
        try:
            _self.DATA = args[1]
        except:
            pass
        _self.__dict__.update(kwargs)
        if _self.__dict__.has_key("uriresolver"):
            _self.__dict__["uriresolver"] = Pyro4.Proxy(
                _self.__dict__["uriresolver"])
        if _self.__dict__.has_key("nr_remote"):
            print _self.__dict__["nr_remote"]
        if _self.__dict__.has_key("_local"):
            injects = {}
            for deps in _self.__dict__["_local"]:
                injects[utils.get_uri_name(deps).split(".")[
                    1]] = Pyro4.Proxy(deps)
            _self.__dict__.update(injects)
        if _self.__dict__.has_key("_remote"):
            injects = {}
            for deps in _self.__dict__["_remote"]:
                injects[utils.get_uri_name(deps).split(".")[
                    1]] = Pyro4.Proxy(deps)
            _self.__dict__.update(injects)
        if _self.__dict__.has_key("-->"):
            del(_self.__dict__["-->"])
        # print "injections"
        in_function(*args, **kwargs)
    return out_function


def load_node(in_function):
    def out_function(*args, **kwargs):
        _self = args[0]
        _self.__dict__.update(kwargs)
        in_function(*args, **kwargs)
    return out_function


@Pyro4.expose
class Control(object):
    def __init__(self, fn=None, *k, **kw):
        self.fn = []
        self.subscriptors = {}
        if fn == None:
            self.worker_run = False
        self.mutex = threading.Lock()
        if type(fn) not in (list, tuple):
            self.fn.append(fn)
        else:
            self.fn.extend(fn)
        self.workers = []
        for f in self.fn:
            self.init_workers(f)

    def init_workers(self, func):
        if self.worker_run:
            t = threading.Thread(target=func, args=())
            self.workers.append(t)
            t.setDaemon(True)
            t.start()

    def adquire(self):
        self.mutex.adquire()

    def release(self):
        self.mutex.release()

    def stop(self):
        self.worker_run = False

    def echo(self, msg="hello"):
        return msg

    def get_pyroid(self):
        return self.pyro4id

    def send_subscripcion(self, obj, key):
        try:
            obj.subscribe(key, self.pyro4id)
        except:
            print("ERROR: in subscripcion %s URI: %s" % (obj, key))

    def subscribe(self, key, uri):
        try:
            self.subscriptors[key] = Pyro4.Proxy(uri)
            #print ("arduino subcriptor %s %s" %(key,uri))
            return True
        except:
            return False

    @Pyro4.oneway
    def publication(self, key, value):
        try:
            setattr(self, key, value)
        except:
            pass
