import socket
import fcntl
import struct
import Pyro4
import Pyro4.naming as nm
import netifaces as ni

def get_ip_address(ifname="lo"): #necesita netifaces pero se comporta mejor en raspberry
  try:
    ni.ifaddresses(ifname)
    ip=ni.ifaddresses(ifname)[2][0]['addr']
  except:
    raise
    ip="127.0.0.1"
  return ip

def free_port(port,ip="127.0.0.1"):
    lo="127.0.0.1"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
       s.connect((ip, int(port)))
       s.shutdown(2)
       return False
    except:
       return True


def URI_split(uri):
    name=uri[uri.find("PYRO:")+5:uri.find("@")]
    ip=uri[uri.find("@")+1:uri.find(":",7)]
    port=int(uri[uri.find(":",7)+1:])
    return (name,ip,port)

def get_uri(name,ip,port):
    return "PYRO:"+name+"@"+ip+":"+str(port)

def get_uri_name(uri):
    return uri[uri.find("PYRO:")+5:uri.find("@")]
