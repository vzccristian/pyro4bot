from multiprocessing.connection import Listener
from threading import Thread
import pickle

class RPCHandler:
    def __init__(self):
        self._functions = { }
    def register_function(self, func):
        self._functions[func.__name__] = func
    def handle_connection(self, connection):
        try:
            while True:
                # Receive a message
                func_name, args, kwargs = pickle.loads(connection.recv())
                # Run the RPC and send a response
                try:
                    r = self._functions[func_name](*args,**kwargs)
                    connection.send(pickle.dumps(r))
                except Exception as e:
                    connection.send(pickle.dumps(e))
        except EOFError:
                pass

def rpc_server(handler, address, authkey):
     sock = Listener(address, authkey=authkey)
     while True:
         client = sock.accept()
         t = Thread(target=handler.handle_connection, args=(client,))
         t.daemon = True
         t.start()
