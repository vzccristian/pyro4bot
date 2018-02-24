#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________

import threading
from _client_robot import ClientRobot
import time
import Pyro4
import cv2
import urllib
import numpy as np
from PIL import Image
import io
import socket
import struct
import time


def run_camera(cam):
    print "Run_camera"
    #Creacion socket en server
    port=cam.image
    print "Client port: "+str(port)
    client_socket = socket.socket()
    client_socket.connect(('158.49.247.167', port))
    makefilename="make"+str(port);
    print makefilename
    connection = client_socket.makefile(makefilename)

    try:
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                print "No image len"
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)

            #BytesIO
            data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
            c2 = cv2.imdecode(data, 1)

            #centro=[]
            #centro,img=track(c)
            cv2.imshow('learnbot2',c2)
            cv2.waitKey(0)
            if cv2.waitKey(1) == 27:
               exit(0)

            # image = Image.open(image_stream)
            # print('Image is %dx%d' % image.size)
            # image.verify()
            # print('Image is verified')
    finally:
        print ("Exit")
        connection.close()
        client_socket.close()

bot=ClientRobot("learnbot1") #nombre del bot en la name no el fichero json
print "Bot adquirido."
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()

time.sleep(2)

while True:
    time.sleep(0.05)
