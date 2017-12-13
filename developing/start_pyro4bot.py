# buscar ip raspberry
# sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
# dmesg | grep FTDI

import node.node as nodo
import time
import sys
from bigbrother import pyro4bot_NS as ns
import threading


ns = threading.Thread(target=ns.start,args=())
ns.start()


if len(sys.argv) > 1:
    jsonbot = sys.argv[1]
else:
    jsonbot = "./samples/simplebot"
nod = nodo.NODERB(filename=jsonbot)

ns.join()
