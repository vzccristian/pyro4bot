#!/usr/bin/python
import bluetooth
from subprocess import Popen, PIPE
import sys


def GetFirstMAC():
    proc = Popen(['hcitool', 'dev'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = proc.communicate()
    if proc.returncode == 0:
        lines = output.split('\r')
        for line in lines:
            if 'hci0' in line:
                temp = line.split('\t')
                temp = temp[2].strip('\n')
                return temp
        raise Exception('MAC not found')
    else:
        raise Exception('Command: {0} returned with error: {1}'.format(cmd, error))


class bt_RFCOMM(object):
    def __init__(self, port=3333, receiveSize=1024):
        self.btSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._ReceiveSize = receiveSize
        self.port = port

    def __exit__(self):
        self.Disconnect()

    def Connect(self, mac):
        try:
            self.btSocket.connect((mac, self.port))
        except:
            print("ERROR bluetooth connects")

    def Disconnect(self):
        try:
            self.btSocket.close()
        except Exception:
            pass

    def Discover(self):
        self.btDevices = bluetooth.discover_devices(lookup_names=True)
        if len(self.btDevices) > 0:
            return self.btDevices
        else:
            return None

    def DumpDevices(self):
        for mac, name in self.btDevices:
            print("BT device name: {0}, MAC: {1}".format(name, mac))

    def BindListen(self, mac, port=8000, backlog=1):
        self.btSocket.bind((mac, port))
        self.btSocket.listen(backlog)

    def Accept(self):
        client, clientInfo = self.btSocket.accept()
        return client, clientInfo

    def Send(self, data):
        self.btSocket.send(data)

    def Receive(self):
        return self.btSocket.recv(self._ReceiveSize)

    def GetReceiveSize(self):
        return self._ReceiveSize


class BTClient(object):
    def __init__(self, mac, name=None, port=8000):
        self.port = port
        self.mac = mac
        self.client = bt_RFCOMM(self.port)
        self.client.Connect(mac)

    def sendData(self, data=None):
        try:
            if data is not None:
                self.client.Send(data)
        except:
            print("ERROR in BTClient send")

    def DumpDevices(self):
        self.client.DumpDevices()

    def Discover(self):
        self.client.Discover()

    def __exit__(self):
        self.client.Disconnect()


class BTServer(object):
    def __init__(self, port):
        self.port = port
        self.srv = bt_RFCOMM(port)
        self.mac = GetFirstMAC()
        self.srv.BindListen(self.mac)
        self.data = None

    def start(self):
        while True:
            print("start")
            self.client, self.clientInfo = self.srv.Accept()
            try:
                while True:
                    self.data = self.client.recv(self.srv.GetReceiveSize())
                    print("data: ", self.data)
            except:
                print("clossing", self.clientInfo)
                self.client.close()
        self.srv.Disconnect()

    def sendData(self):
        if self.data is not None:
            self.client.send(data)

    def stop(self):
        self.serv.Disconnect()

    def discover_devices(self):
        return {name: mac for mac, name in self.srv.Discover()}

    def __exit__(self):
        self.serv.Disconnect()


if __name__ == "__main__":
    mac = GetFirstMAC()
    print(mac)
    robot = "B8:27:EB:34:76:BA"
    client = BTClient(robot, "alphabot1", 3333)
    client.DumpDevices()
    # for i in range(500):
    #     client.sendData("paco"+str(i))
