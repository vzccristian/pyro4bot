import time
import threading
import Pyro4
import utils
import os
import token

#____________________DECORATOR FOR GENERAL CLASS__________________

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

        if "name" in _self.__dict__:
            _self.__dict__["botname"] = _self.__dict__["name"].split(".")[0]
        if "uriresolver" in _self.__dict__:
            _self.__dict__["uriresolver"] = utils.get_pyro4proxy(
                _self.__dict__["uriresolver"], _self.__dict__["name"].split(".")[0])
        if "nr_remote" in _self.__dict__:

            print _self.__dict__["nr_remote"]
        if "_local" in _self.__dict__:
            injects = {}
            for deps in _self.__dict__["_local"]:
                injects[utils.get_uri_name(deps).split(".")[
                    1]] = utils.get_pyro4proxy(deps, _self.__dict__["name"].split(".")[0])
            _self.__dict__.update(injects)
        if "_remote" in _self.__dict__:
            injects = {}
            for deps in _self.__dict__["_remote"]:
                injects[utils.get_uri_name(deps).split(".")[
                    1]] = utils.get_pyro4proxy(deps, _self.__dict__["name"].split(".")[0])
            _self.__dict__.update(injects)
        if "-->" in _self.__dict__:
            del(_self.__dict__["-->"])
        super(_self.__class__.__mro__[0], _self).__init__()
        in_function(*args, **kwargs)

    return out_function


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

    def __init__(self, *k, **kw):
        self.threadpublisher = False
        self.workers = []
        self.token_data = None
        self.subscriptors = {}
        self.mutex = threading.Lock()

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
        if isinstance(token_data, token.Token):
            self.threadpublisher = True
            t = threading.Thread(target=self.thread_publisher,
                                 args=(token_data, frec))
            self.workers.append(t)
            t.setDaemon(True)
            t.start()
        else:
            print "Can not publish to object other than token"

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
            print "Me subscribo a:",obj,key
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
