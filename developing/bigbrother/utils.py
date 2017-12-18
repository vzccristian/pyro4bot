import socket
import fcntl
import struct
import Pyro4
import Pyro4.naming as nm
import netifaces as ni
from termcolor import colored
import threading

def get_ip_address(ifname="lo"):  # necesita netifaces pero se comporta mejor en raspberry
    try:
        ni.ifaddresses(ifname)
        ip = ni.ifaddresses(ifname)[2][0]['addr']
    except:
        # raise
        ip = "localhost"
    return ip


def uri_split(uri):
    name = uri[uri.find("PYRO:") + 5:uri.find("@")]
    ip = uri[uri.find("@") + 1:uri.find(":", 7)]
    port = int(uri[uri.find(":", 7) + 1:])
    return (name, ip, port)


def get_uri(name, ip, port):
    return "PYRO:" + name + "@" + ip + ":" + str(port)


def get_uri_name(uri):
    return uri[uri.find("PYRO:") + 5:uri.find("@")]

def printThread(color="green"):
    return ((colored("[" + threading.current_thread().getName() + "]", color)))
