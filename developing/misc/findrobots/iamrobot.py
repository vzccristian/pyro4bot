import sys
import socket
import netifaces as ni
import time
PORT = 56665


def get_all_ip_address():
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
                    if not ips["addr"].startswith("127."):
                        address.append(ips["addr"])
            except Exception:
                pass
    except Exception:
        #print("ERROR: get_all_ip_address()")
        return None
    return address

class Robot():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', PORT))
        # print('{} -> listening on port: {}'.format(get_all_ip_address()
                                                  # [0], self.s.getsockname()[1]))
        self.listener()


    def listener(self):
        while 1:
            data, wherefrom = self.s.recvfrom(1500, 0)
            if data=="hi pyro4bot":
                # print("From: {}:{} --> {}".format(
                #     wherefrom[0], wherefrom[1], data))
                self.s.sendto(str(socket.gethostname() + "/" + " hello "),
                     (wherefrom[0], wherefrom[1]))
            time.sleep(1)


if __name__ == '__main__':
    Robot()
