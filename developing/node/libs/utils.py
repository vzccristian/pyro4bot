import Pyro4
import netifaces as ni
import traceback
import sys
from termcolor import colored
import threading
import os
import socket


def get_ip_address(ifname="lo"):  # necesita netifaces pero se comporta mejor en raspberry
    try:
        ip = ni.ifaddresses(ifname)[2][0]['addr']
    except Exception:
        try:
            interface_list = ni.interfaces()
            for x in interface_list:
                if (x.find("lo") < 0):
                    return ni.ifaddresses(x)[2][0]['addr']
            ip = "127.0.0.1"
        except Exception:
            print("Error al extraer IP de la interfaz "
                  + colored(ifname, "red"))
            sys.exit()
    return ip

def get_all_ip_address():
    address = []
    try:
        for x in ni.interfaces():
            add = ni.ifaddresses(x)
            try:
                for ips in add[ni.AF_INET]:
                    address.append(ips["addr"])
            except Exception:
                pass
    except Exception:
        print "Error in utils.get_all_ip_address()"
        raise
        exit()
    return address

def get_gateway_address(ifname="lo"):
    ip = None
    try:
        gateway_list = ni.gateways()
        for gw in gateway_list[2]:
            if gw[1] is ifname:
                ip = gw[0]
                break
    except Exception:
        raise
    return ip


def free_port(port, ip="127.0.0.1"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return False
    except Exception:
        return True


def get_free_port(port, interval=1, ip="127.0.0.1"):
    _port = port
    while not free_port(_port, ip=ip):
        _port += interval
    return (_port)


def uri_split(uri):
    name = uri[uri.find("PYRO:") + 5:uri.find("@")]
    ip = uri[uri.find("@") + 1:uri.find(":", 7)]
    port = int(uri[uri.find(":", 7) + 1:])
    return (name, ip, port)


def get_uri(name, ip, port):
    return "PYRO:" + name + "@" + ip + ":" + str(port)


def get_uri_name(uri):
    return uri[uri.find("PYRO:") + 5:uri.find("@")]


def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(
        sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)

    exception_str = exception_str[:-1]

    return exception_str


def printThread(string, color="green"):
    print(
        (colored("[" + threading.current_thread().getName() + "] ", color)) + string)


def ping(uri):
    response = False
    try:
        response = os.system("ping -c 1 -w2 " + uri + " > /dev/null 2>&1")
    except Exception:
        pass
    return (not response)


def get_pyro4proxy(uri, password):
    proxy = Pyro4.Proxy(uri)
    proxy._pyroHmacKey = bytes(password)
    return proxy
