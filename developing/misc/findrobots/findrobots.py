#!/usr/bin/env python
import sys
import time
import threading
import socket
import netifaces as ni

# Send UDP broadcast packets

PORT = 56665
TIMEOUT = 5

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
        print("ERROR: get_all_ip_address()")
        raise
        exit()
    return address


class Searcher():
    def __init__(self):
        self.robots = {}
        self.stop = threading.Event()
        self.socket_list = []
        try:
            interface_list = ni.interfaces()
            interface_list.remove("lo")
            interfaces = zip(
                interface_list, get_all_ip_address(broadcast=True))
            n = 0
            for interface in interfaces:
                threading.Thread(target=self.send, args=(
                    self.stop, interface, n)).start()
                time.sleep(1)
                threading.Thread(target=self.locate,
                                 args=(self.stop, n)).start()
                n += 1
        except Exception:
            raise
            pass
        time.sleep(TIMEOUT)
        self.stop.set()

    def send(self, stop_event, interface, n):
        self.socket_list.append(socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM))
        self.socket_list[n].bind(('', 0))
        self.socket_list[n].setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, interface[0] + '\0')
        self.socket_list[n].settimeout(TIMEOUT + 1)
        # print('sending to: {}'.format(PORT))
        while (not stop_event.is_set()):
            self.data = 'hi pyro4bot'
            self.socket_list[n].sendto(self.data, (interface[1], PORT))
            time.sleep(1)

    def locate(self, stop_event, n):
        # print self.socket_list[n].getsockname()
        # print('listening from port: {}'.format(self.socket_list[n].getsockname()[1]))
        while (not stop_event.is_set()):
            try:
                data, wherefrom = self.socket_list[n].recvfrom(1500, 0)
                self.robots[wherefrom] = data
            except socket.timeout:
                pass


if __name__ == '__main__':
    s = Searcher()
    for r in s.robots.iteritems():
        print r
