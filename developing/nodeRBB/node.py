#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________
import sys
import os
import time
import pprint
from LIBS import Conf,control,utils
from LIBS.exceptions import Errornode
from multiprocessing import Process, Pipe
import traceback
import Pyro4
import Pyro4.naming as nm
from termcolor import colored

def IMPORT_CLASS(list_class):
    try:
      list_class.append(("SERVICES","URI_resolver","URI_resolver")) #mejor cambiar
      print "____________IMPORTING CLASS_______________________"
      for c in sorted(list_class):
          print "CLASS %s: from %s import %s" % (c[2],c[0],c[1])
          exec("from %s import %s" % (c[0],c[1]), globals())
    except:
        print "ERROR IMPORTING CLASS:",c[0]+"/"+c[1]+"."+c[2]
        traceback.print_exc()
        exit(0)

def Remote_Object(d):
    (name_ob,ip,ports)=utils.URI_split(d["pyro4id"])
    uriprint="error"
    try:
      daemon = Pyro4.Daemon(host=ip,port=ports)
      uri = daemon.register(eval(d["cls"])(data=[],**d),objectId=name_ob)
      uriprint=uri.asString()
      daemon.requestLoop()
    except Exception:
      print("ERROR: creating server object"+uriprint)
      raise
    finally:
      print("[%s] Shuting %s"% (colored("Down",'green'),uriprint))

#___________________CLASS NODERB________________________________________


class NODERB (object):
    def __init__(self,filename="",json={}): #revisar la carga posterion de parametros json
        self.filename=filename
        self.N_conf=Conf.Conf(filename=filename,json=json)
        self.load_node(self,PROCESS={},**self.N_conf.NODE)
        IMPORT_CLASS(self.N_conf.module_cls())
        self.URI_resolv=self.load_uri_resolver()
        self.URI=Pyro4.Proxy(self.URI_resolv)
        self.load_robot()
        self.create_server_node()


    @control.loadnode
    def load_node(self,data,**kwargs):
        print ("NOTIFIER:Starting System PyRobot on Ethernet device %s IP: %s"% (colored(self.ethernet,'yellow'),colored(self.ip,'yellow')))
        print ("NOTIFIER:Node config loaded for filename:%s" % (colored(self.filename,'yellow')))
        self.PROCESS={}
        self.ROBOT=self.N_conf.ROBOT
        Pyro4.config.SERIALIZERS_ACCEPTED=set(['pickle','json', 'marshal', 'serpent'])

    def load_uri_resolver(self):
        name=self.name+".URI_resolv"
        loader=self.N_conf.NODE[name]
        while not utils.free_port(self.port_node+1):
            self.port_node+=10
        loader["pyro4id"]="PYRO:"+name+"@"+"127.0.0.1"+":"+str(self.port_node+1)
        self.PROCESS[name]=[]
        self.PROCESS[name].append(loader["pyro4id"])
        self.PROCESS[name].append(Process(name=name, target=Remote_Object,args=(loader,)))
        self.PROCESS[name][1].start()
        self.PROCESS[name].append(self.PROCESS[name][1].pid)
        self.URI=Pyro4.Proxy(loader["pyro4id"])
        conect=False
        while not conect :
          try:
            conect=self.URI.echo()=="hello"
          except:
            conect=False
          time.sleep(0.3)
        if conect:
          self.PROCESS[name].append("OK")
          print "___________STARTING RESOLVER URIs___________________"
          print("URI %s" %(colored(loader["pyro4id"],'green')))
          if self.URI.get_ns():
              print("NAME SERVER LOCATED. %s"% (colored(" Resolving remote URIs ",'green')))
          else:
              print("NAME SERVER NOT LOCATED. %s" % (colored(" Resolving only LOCAL URIs ",'green')))
          return loader["pyro4id"]
        else:
           self.PROCESS[name].append("DOWN")
           return None

    def create_server_node(self):
        Pyro4.config.HOST=self.ip
        try:
            #si hay nameserver registar todos los proxys y el SERVER
            daemon = Pyro4.Daemon(host=self.ip,port=self.port_node)
            uri = daemon.register(self,objectId=self.name)
            print ("____________STARTING PYRO4BOT %s_______________________" % self.name)
            print ("[%s]  PYRO4BOT: %s" %(colored("OK",'green'),uri))
            self.URI.register_robot(uri)
            self.print_process()
            daemon.requestLoop()
            try:
               ns=Pyro4.locateNS()
               ns.remove(self.name)
            except:
               pass
        except:
            print("ERROR: in PYRO4BOT")
            #raise
        finally:
            print("[%s] Shuting %s"% (colored("Down",'green'),uri.asString()))

    def load_robot(self):
        print "____________STARTING PYRO4BOT OBJECT_______________________"
        for k in self.N_conf.whithout_deps():
            self.Start_Object(k,self.ROBOT[k])
        object_robot=self.N_conf.with_deps()
        for k in object_robot:
            self.ROBOT[k]["_local_trys"]=25
            self.ROBOT[k]["_remote_trys"]=5
        #print object_robot
        while object_robot!=[]:
              k=object_robot.pop(0)
              self.ROBOT[k]["nr_local"],self.ROBOT[k]["nr_remote"]=self.N_conf.local_remote(k)
              st_local,st_remote=self.check_deps(k)
              if st_local=="ERROR":
                  print "[%s]  STARTING %s Error in locals %s" % (colored(st_local,'red'),k,self.ROBOT[k]["nr_local"])
                  continue
              if st_remote=="ERROR":
                  print "[%s]  STARTING %s Error in remotes %s" % (colored(st_remote,'red'),k,self.ROBOT[k]["nr_remote"])
                  continue

              if st_local=="WAIT" or st_remote=="WAIT":
                  object_robot.append(k)
                  continue
              if st_local=="OK":
                  del(self.ROBOT[k]["nr_local"])
                  del(self.ROBOT[k]["_local_trys"])
                  if st_remote=="OK":
                    del(self.ROBOT[k]["_remote_trys"])
                    del(self.ROBOT[k]["nr_remote"])
                  self.ROBOT[k]["_REMOTE_STATUS"]=st_remote
                  self.Start_Object(k,self.ROBOT[k])


    def check_local_deps(self,obj):
        check_local="OK"
        for d in obj["nr_local"]:
            uri= self.URI.wait_available(d)
            if uri!=None:
              obj["_local"].append(uri)
            else:
               obj["_local_trys"]-=1
               if obj["_local_trys"]<0:
                  check_local="ERROR"
                  break
               else:
                  check_local="WAIT"
                  break
        return check_local

    def check_remote_deps(self,obj):
        check_remote="OK"
        for d in obj["nr_remote"]:
            uri=self.URI.wait_resolv_remotes(d)
            if uri==None:
                check_remote="ERROR"
                break
            if uri==d:
                obj["_remote_trys"]-=1
                if obj["_remote_trys"]<0:
                   check_remote="WAITING"
                   break
                else:
                    check_remote="WAIT"
                    break
            else:
                obj["_remote"].append(uri)
        return check_remote

    def check_deps(self,k):
        self.ROBOT[k]["_local"]=[]
        self.ROBOT[k]["_remote"]=[]
        check_local=self.check_local_deps(self.ROBOT[k])
        check_remote=self.check_remote_deps(self.ROBOT[k])
        return check_local,check_remote

    def Start_Object(self,name,obj):
        serv_pipe,client_pipe=Pipe()
        if not obj.has_key("_local"):
            obj["_local"]=[]
        if not obj.has_key("_remote"):
            obj["_remote"]=[]
        if not self.PROCESS.has_key(name):
           self.PROCESS[name]=[]
           obj["pyro4id"]=self.URI.new_uri(name,obj["mode"])
           obj["name"]=name
           obj["URI_resolver"]=self.URI_resolv
           self.PROCESS[name].append(obj["pyro4id"])
           self.PROCESS[name].append(Process(name=name, target=self.Pyro4bot_Object,args=(obj,client_pipe,)))
           self.PROCESS[name][1].start()
           self.PROCESS[name].append(self.PROCESS[name][1].pid)
           status=serv_pipe.recv()
           self.PROCESS[name].append(status)
           if status=="OK":
               st=colored(status,'green')
           if status=="FAIL":
               st=colored(status,'red')
           if status=="WAITING":
               st=colored(status,'yellow')
           print "[%s]  STARTING %s" % (st,obj["pyro4id"])
        else:
           print ("ERROR: "+name+" is runing")

    def Pyro4bot_Object(self,d,proc_pipe):
        (name_ob,ip,ports)=utils.URI_split(d["pyro4id"])
        try:
            daemon = Pyro4.Daemon(host=ip,port=ports)
            uri = daemon.register(eval(d["cls"])(data=[],**d),objectId=name_ob)
            if d.has_key("_REMOTE_STATUS") and d["_REMOTE_STATUS"]=="WAITING":
                proc_pipe.send("WAITING")
            else:
                proc_pipe.send("OK")
            daemon.requestLoop()
            print("[%s] Shuting %s"% (colored("Down",'green'),d["pyro4id"]))
        except:
            proc_pipe.send("FAIL")
            print("  ERROR: creating Robot object"+d["pyro4id"])
            raise


    @Pyro4.expose
    def get_URIS(self):
          pet=[self.PROCESS[x][0] for x in self.PROCESS]
          print self.URI.list_uris()
          return self.URI.list_uris()
    @Pyro4.expose
    def get_name_uri(self,name):
        #print self.URI.list_uris()
        if self.PROCESS.has_key(name):
            uri=self.URI.get_uri(name)
            status=self.PROCESS[name][3]
            return uri,status
        else:
            return None, "down"
    @Pyro4.expose
    def print_process(self):
        for k,v in self.PROCESS.iteritems():
            name=v[0]
            pid=str(v[2])
            status=str("["+colored(v[3],'green')+"]")
            print(status.ljust(17," ")+pid+name.rjust(50,"."))



if __name__ == "__main__":

    print("STARTING NODERB")
