import pickle
from multiprocessing.connection import Client
import time


class RPCProxy:
    def __init__(self, connection):
        self._connection = connection

    def __getattr__(self, name):
        def do_rpc(*args, **kwargs):
            self._connection.send(pickle.dumps((name, args, kwargs)))
            result = pickle.loads(self._connection.recv())
            if isinstance(result, Exception):
                raise result
            return result

        return do_rpc


if __name__ == "__main__":
    print("Client")
    c = Client(('localhost', 17000), authkey=b'PyRobot')
    proxy = RPCProxy(c)
    proxy.request("*.camera")

    print("Lista:", (proxy.list()))
    time.sleep(1)
    bot = proxy.proxy("learnbot1")
    if bot is not None:
        print("Learnbot1", (bot.get_uris()))

    time.sleep(3)
    proxy.remove("learnbot1")
    print("Lista despues de remove", (proxy.list()))
