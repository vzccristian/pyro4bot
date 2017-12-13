import Pyro4
import Pyro4.naming as nm
import utils

def start():
    print "Checking name_server"
    try:
        # Working
        ns = Pyro4.locateNS()

    except:
        createNameServer()
        # Not working




def createNameServer(ethernet="eth0"):
    print "Creating new name server"
    try:
        nm.startNS(host=utils.get_ip_address(ethernet))
    except:
        raise
    finally:
        nm.stopNS() 
