#buscar ip raspberry
#sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
#dmesg | grep FTDI

import nodeRBB.node as nodo
import time
import sys

if len(sys.argv)>1:
    jsonbot=sys.argv[1]
else:
    jsonbot="./simplebot"
nod=nodo.NODERB(filename=jsonbot)
