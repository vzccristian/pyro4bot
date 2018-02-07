import pickle
from multiprocessing.connection import Client
import time

class RPCProxy:
    def __init__(self,ip="localhost",port=17000,authKey="PyRobot"):
        self._connection = Client((ip, port), authkey=bytes(authKey))

    def __getattr__(self, name):
        def do_rpc(*args, **kwargs):
            self._connection.send(pickle.dumps((name, args, kwargs)))
            result = pickle.loads(self._connection.recv())
            if isinstance(result, Exception):
                raise result
            return result
        return do_rpc
