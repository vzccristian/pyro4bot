import Pyro4


class clientNODERB(object):
    def __init__(self,name):
        self.name=name
        try:
          self.node=Pyro4.Proxy("PYRONAME:"+name)
          self.proxys=self.node.list_process()
          for p in self.proxys:
              if p.find(".")!=-1:
                (prx,con)=p.split(".")
                setattr(self,con,Pyro4.Proxy("PYRONAME:"+p))
        except:
          print("ERROR: conection")
          raise
          exit()
