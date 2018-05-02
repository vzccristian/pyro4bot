"""Utils to PYRO4BOT."""

import Pyro4
import netifaces as ni
import traceback
import sys
from termcolor import colored
import threading
import os
import socket


def get_ip_address(ifname="lo"):
    """Return IP address from a specific interface."""
    try:
        ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    except Exception:
        #  Invalid interface name
        try:
            interface_list = ni.interfaces()
            for x in interface_list:
                if (x != "lo"):
                    return ni.ifaddresses(x)[ni.AF_INET][0]['addr']
            ip = "127.0.0.1"
        except Exception:
            print("ERROR: Obtaining IP from the network interface. "
                  + colored(ifname, "red"))
            sys.exit()
    return ip


def get_all_ip_address(broadcast=False):
    """Return the list of IPs of all network interfaces.

    If broadcast = True, returns the list of broadcast IPs of all network
    interfaces.
    """
    address = []
    try:
        for x in ni.interfaces():
            add = ni.ifaddresses(x)
            try:
                for ips in add[ni.AF_INET]:
                    if broadcast:
                        address.append(ips["broadcast"])
                    else:
                        address.append(ips["addr"])
            except Exception:
                pass
    except Exception:
        print("ERROR: utils.get_all_ip_address()")
        raise
        exit()
    return address


def get_gateway_address(ifname="lo"):
    """Return gateway address from a specific interface."""
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


def get_interface():
    """Return the name of the first network interface other than loopback."""
    interface = None
    loopback = None
    try:
        for x in ni.interfaces():
            try:
                if ni.ifaddresses(x)[ni.AF_INET][0]['addr'] != "127.0.0.1":
                    interface = x
                    break
                else:
                    loopback = x
            except Exception:
                pass
    except Exception:
        raise

    if not interface:
        interface = loopback

    return interface


def free_port(port, ip="127.0.0.1"):
    """Return True if the port is free at a specific IP address, otherwise \
    return False."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return False
    except Exception:
        return True


def get_free_port(port, interval=1, ip="127.0.0.1"):
    """Return free port from a specific IP."""
    _port = port
    while not free_port(_port, ip=ip):
        _port += interval
    return (_port)


def uri_split(uri):
    """Split Pyro4 URI in name, ip and port."""
    name = uri[uri.find("PYRO:") + 5:uri.find("@")]
    ip = uri[uri.find("@") + 1:uri.find(":", 7)]
    port = int(uri[uri.find(":", 7) + 1:])
    return (name, ip, port)


def get_uri(name, ip, port):
    """Return the Pyro4 URI formed from name, ip and port."""
    return "PYRO:" + name + "@" + ip + ":" + str(port)


def get_uri_name(uri):
    """Return name from Pyro4 URI."""
    return uri[uri.find("PYRO:") + 5:uri.find("@")]


def get_uri_base(uri):
    """ return base component from Pyro4 URI """
    return get_uri_name(uri).split(".")[1]


def format_exception(e):
    """Representation of exceptions."""
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
    """Print on console the thread that executes the code and the text \
    passed by parameter."""
    print(
        (colored("[" + threading.current_thread().getName() + "] ", color)
         ) + string)


def ping(uri):
    """Ping and return True if there is connection, False otherwise."""
    response = False
    try:
        response = os.system("ping -c 1 -w2 " + uri + " > /dev/null 2>&1")
    except Exception:
        pass
    return (not response)


def get_pyro4proxy(uri, password):
    """Given a Pyro4 URI and a password, return the connection proxy."""
    proxy = Pyro4.Proxy(uri)
    proxy._pyroHmacKey = bytes(password)
    return proxy


def get_con_proxy(uri, password):
    return get_uri_base(uri), get_pyro4proxy(uri, password)


def prepare_proxys(part, password):
    injects = {}
    part["deps"] = {}
    if "name" in part:
        part["botname"], part["name"] = part["name"].split(".")
    if "uriresolver" in part:
        part["uriresolver"] = get_pyro4proxy(part["uriresolver"], password)
    if "node" in part:
        part["node"] = get_pyro4proxy(part["node"], password)
    for d in part.get("_locals", []):
        con, proxy = get_con_proxy(d, password)
        injects[con] = proxy
    for d in part.get("_resolved_remote_deps", []):
        part["deps"][d] = get_pyro4proxy(d, password)
    for d in part.get("_services", []):
        con, proxy = get_con_proxy(d, password)
        injects[con] = proxy

    part.update(injects)
    return part
