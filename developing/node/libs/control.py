import threading
import Pyro4
import utils
import os
import time
import token


# decoradores para las clases generales
def load_config(in_function):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control """
    def out_function(*args, **kwargs):
        _self = args[0]
        try:
            _self.DATA = args[1]
        except Exception:
            pass
        _self.__dict__.update(kwargs)
        super(_self.__class__.__mro__[0], _self).__init__()
        in_function(*args, **kwargs)
    return out_function


def Pyro4bot_Loader(cls,kwargs):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control
    """
    original_init = cls.__init__
    def init(self):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(cls,self).__init__()
        original_init(self)
    cls.__init__ = init
    return cls


def load_node(in_function):
    """this Decorator load all parameter defined in Json configuration in node object """
    def out_function(*args, **kwargs):

        _self = args[0]
        _self.__dict__.update(kwargs)
        in_function(*args, **kwargs)
    return out_function


class Control(object):
    """ This class provide threading funcionality to all object in node.
        Init workers Threads and PUB/SUB thread"""

    def __init__(self):
        self.mutex = threading.Lock()
        self.workers = []

    def init_workers(self, fn):
        """ start all workers daemon"""

        if type(fn) not in (list, tuple):
            fn = (fn,)
        if self.worker_run:
            for func in fn:
                t = threading.Thread(target=func, args=())
                self.workers.append(t)
                t.setDaemon(True)
                t.start()

    def init_publisher(self, token_data, frec=0.01):
        """ start publisher daemon"""
        self.threadpublisher = False
        self.token_data = None
        self.subscriptors = {}
        if isinstance(token_data, token.Token):
            self.threadpublisher = True
            t = threading.Thread(target=self.thread_publisher,
                                 args=(token_data, frec))
            self.workers.append(t)
            t.setDaemon(True)
            t.start()
        else:
            print("ERROR: Can not publish to object other than token")

    def thread_publisher(self, token_data, frec):
        """ public data between all subcriptors in list"""
        while self.threadpublisher:
            d = token_data.get_attribs()
            try:
                for key in self.subscriptors.keys():
                    subscriptors = self.subscriptors[key]
                    try:
                        if key in d:
                            for item in subscriptors:
                                # print("publicando",key, d[key])
                                item.publication(key, d[key])
                    except TypeError:
                        print "Argumento no esperado."
                        raise
                        exit()
            except Exception as e:
                print utils.format_exception(e)
                raise
            time.sleep(frec)


    @Pyro4.expose
    def send_subscripcion(self, obj, key):
        """ send a subcripcion request to an object"""
        try:
            obj.subscribe(key, self.pyro4id)
        except Exception:
            print("ERROR: in subscripcion %s URI: %s" % (obj, key))
            raise
            return False

    @Pyro4.expose
    def subscribe(self, key, uri):
        """ receive a request for subcripcion from an object and save data in dict subcriptors
            Data estructure store one item subcripcion (key) and subcriptors proxy list """
        try:
            if key not in self.subscriptors:
                self.subscriptors[key] = []
            proxy = self.__dict__["uriresolver"].get_proxy(uri)
            self.subscriptors[key].append(proxy)
            return True
        except Exception:
            print("ERROR: in subscribe")
            raise
            return False

    @Pyro4.oneway
    @Pyro4.expose
    def publication(self, key, value):
        """ is used to public in this object a item value """
        try:
            # print("setattr",key,value)
            setattr(self, key, value)
        except Exception:
            raise

    def adquire(self):
        self.mutex.adquire()

    def release(self):
        self.mutex.release()

    def stop(self):
        self.worker_run = False

    @Pyro4.expose
    def echo(self, msg="hello"):
        return msg

    @Pyro4.expose
    def get_pyroid(self):
        return self.pyro4id

    @Pyro4.expose
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring

    @Pyro4.expose
    def get_class(self):
        return self._dict__[cls]
