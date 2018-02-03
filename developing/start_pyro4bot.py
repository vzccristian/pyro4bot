# buscar ip raspberry
# sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
# dmesg | grep FTDI

import node.node as nodo
import time
import sys

def start_pyro4bot(json="./samples/simplebot"):
    nod = nodo.NODERB(filename=json)

if __name__ == '__main__':
    start_pyro4bot()
    
