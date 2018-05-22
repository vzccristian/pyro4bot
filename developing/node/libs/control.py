import Pyro4
import utils
import time
import token
import threading
from threading import Thread
from termcolor import colored
from botlogging import botlogging


SECS_TO_CHECK_STATUS = 5

# DECORATORS

# Threaded function snippet
def threaded(fn):
    """To use as decorator to make a function call threaded."""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


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


def Pyro4bot_Loader(clss, **kwargs):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control
    """
    original_init = clss.__init__

    def init(self):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(clss, self).__init__()
        original_init(self)
    clss.__init__ = init
    return clss


def flask(*args_decorator):
    def flask_decorator(func):
        original_doc = func.__doc__
        if func.__doc__ is None:
            original_doc = ""
        if len(args_decorator) % 2 == 0:  # Tuplas
            for i in xrange(0, len(args_decorator), 2):
                original_doc += "\n@type:" + \
                    args_decorator[i] + "\n@count:" + \
                    str(args_decorator[i + 1])
        elif len(args_decorator) == 1:
            original_doc += "\n @type:" + \
                args_decorator[0] + "\n@count:" + \
                str(func.__code__.co_argcount - 1)

        if "@type:actuator" in original_doc:
            li = list(func.__code__.co_varnames)
            del li[0]
            original_doc += "\n@args_names:" + str(li)

        func.__doc__ = original_doc

        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func_wrapper.__doc__ = original_doc
        return func_wrapper
    return flask_decorator


class Control(botlogging.Logging):
    """ This class provide threading funcionality to all object in node.
        Init workers Threads and PUB/SUB thread"""

    def __init__(self):
        super(Control,self).__init__()
        self.mutex = threading.Lock()
        self.workers = []
        if "worker_run" not in self.__dict__:
            self.worker_run = True

    def __check_start__(self):
        while (self._REMOTE_STATUS != "OK" or
               (self._REMOTE_STATUS == "ASYNC" and
                not self._resolved_remote_deps)):
            time.sleep(SECS_TO_CHECK_STATUS)

    @threaded
    def init_workers(self, fn):
        """ Start all workers daemon"""
        self.__check_start__()
        if type(fn) not in (list, tuple):
            fn = (fn,)
        if self.worker_run:
            for func in fn:
                t = threading.Thread(target=func, args=())
                self.workers.append(t)
                t.setDaemon(True)
                t.start()
            return t

    @threaded
    def init_thread(self, fn, *args):
        """ Start all workers daemon"""
        self.__check_start__()
        if self.worker_run:
            t = threading.Thread(target=fn, args=args)
            self.workers.append(t)
            t.start()

    @threaded
    def init_publisher(self, token_data, frec=0.01):
        """ Start publisher daemon"""
        self.__check_start__()
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
            print(
                "ERROR: Can not publish to object other than token {}".format(token_data))

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
                        print("Invalid argument.")
                        raise
                        exit()
            except Exception as e:
                print utils.format_exception(e)
                raise
            time.sleep(frec)

    @Pyro4.expose
    def send_subscripcion(self, obj, key):
        """ Send a subcripcion request to an object"""
        try:
            obj.subscribe(key, self.pyro4id)
        except Exception:
            print("ERROR: in subscripcion %s URI: %s" % (obj, key))
            raise
            return False

    @Pyro4.expose
    def subscribe(self, key, uri):
        """ Receive a request for subcripcion from an object and save data in dict subcriptors
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
        """ Is used to public in this object a item value """
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

    @Pyro4.expose
    @Pyro4.callback
    def add_resolved_remote_dep(self, dep):
        # print(colored("New remote dep! {}".format(dep), "green"))
        if isinstance(dep, dict):
            k = dep.keys()[0]
            try:
                for u in dep[k]:
                    self.deps[k] = utils.get_pyro4proxy(u, k.split(".")[0])
                self._resolved_remote_deps.append(dep[k])
                if (self._unr_remote_deps is not None):
                    if k in self._unr_remote_deps:
                        self._unr_remote_deps.remove(k)
            except Exception:
                print("Error in control.add_resolved_remote_dep() ", dep)
            self.check_remote_deps()
        else:
            print("Error in control.add_resolved_remote_dep(): No dict", dep)

    def check_remote_deps(self):
        status = True
        if (self._unr_remote_deps is not None and self._unr_remote_deps):
            for unr in self._unr_remote_deps:
                if "*" not in unr:
                    status = False
        for k in self.deps.keys():
            try:
                if (self.deps[k]._pyroHandshake != "hello"):
                    status = False
            except Exception:
                print("Error connecting to dep. ", k)
                status = False

        if (status):
            self._REMOTE_STATUS = "OK"
            try:
                self.node.status_changed()
            except Exception as e:
                print "Error in control.check_remote_deps: "+str(e)

        return self._REMOTE_STATUS

    @Pyro4.expose
    def get_status(self):
        return self._REMOTE_STATUS
