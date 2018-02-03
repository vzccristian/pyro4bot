import time
import threading
import Pyro4
import utils


#____________________DECORATOR FOR GENERAL CLASS__________________
def load_config(in_function):
    """ Decorator for load Json options in sensor a service objects"""
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
    """this Decorator load all parameter defined in Json configuration in node object """
    def out_function(*args, **kwargs):
        _self = args[0]
        _self.__dict__.update(kwargs)
        in_function(*args, **kwargs)
    return out_function


@Pyro4.expose
class Control(object):
    """ This class provide threading funcionality to all object.
        Init workers Threads and PUB/SUB thread"""
    def __init__(self, *k, **kw):
        self.threadpublisher=False
        self.data_publication=None
        self.subscriptors = {}
        self.mutex = threading.Lock()


    def init_workers(self, fn=None):
        """ start all workers daemon"""
        if fn == None:
            self.worker_run = False
        if type(fn) not in (list, tuple):
            fn = (fn,)
        self.workers = []
        if self.worker_run:
            for func in fn:
                t = threading.Thread(target=func, args=())
                self.workers.append(t)
                t.setDaemon(True)
                t.start()

    def init_publisher(self,data_publication,frec=0.001):
        """ start publisher daemon"""
        self.threadpublisher=True
        t = threading.Thread(target=self.thread_publisher, args=(data_publication,frec))
        self.workers.append(t)
        t.setDaemon(True)
        t.start()

    def thread_publisher(self,data_publication, frec):
        """ public data between all subcriptors in list"""
        while self.threadpublisher:
            try:
                #print("subscriptors",self.subscriptors)
                for key, subscriptors in self.subscriptors.iteritems():
                    #print(key,subscriptors)
                    if key in data_publication:
                        for item in subscriptors:
                            item.publication(key, data_publication[key])
            except:
                pass
            time.sleep(frec)

    def send_subscripcion(self, obj, key):
        """ send a subcripcion request to an object"""
        try:
            obj.subscribe(key, self.pyro4id)
        except:
            print("ERROR: in subscripcion %s URI: %s" % (obj, key))
            return False

    def subscribe(self, key, uri):
        """ receive a request for subcripcion from an object and save data in dict subcriptors
            Data estructure store one item subcripcion (key) and subcriptors proxy list """
        try:
            if key not in self.subscriptors:
                self.subscriptors[key]=[]
            self.subscriptors[key].append(Pyro4.Proxy(uri))
            return True
        except:
            print("ERROR: in subscribe")
            return False

    @Pyro4.oneway
    def publication(self, key, value):
        """ is used to public in this object a item value """
        try:
            setattr(self, key, value)
        except:
            pass

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
