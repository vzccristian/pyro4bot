#!/usr/bin/env python
# -*- coding: utf-8 -*-
#____________developed by paco andres____________________

import threading
from nodeproxy import ClientNODERB
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

def track(image):
    print "tracking"
    blur = cv2.GaussianBlur(image, (5,5),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40,70,70])
    upper_green = np.array([80,200,200])
    lower_pink = np.array([147,95,150])
    upper_pink = np.array([227,255,255])
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    bmask = cv2.GaussianBlur(mask, (5,5),0)
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    ctr = (-1,-1)
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
        cv2.circle(image, ctr, 10, (255,0,0))
    return ctr,image

def run_camera(cam):
    print "Run_camera"
    #Creacion socket en server
    port=cam.image
    print "Client port: "+str(port)
    client_socket = socket.socket()
    client_socket.connect(('158.49.247.167', port))
    connection = client_socket.makefile("make"+str(port))

    try:
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

            if not image_len:
                print "No image len"
            print "image_len",image_len
            con_read = connection.read(image_len)
            print "readed"
            image_stream.write(con_read)
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            #BytesIO
            data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
            c = cv2.imdecode(data, 1)
            #centro=[]
            #centro,img=track(c)
            cv2.imshow('learnbot1-'+str(port),c)
            if cv2.waitKey(1) == 27:
               exit(0)
    finally:
        print ("Exit")
        connection.close()
        client_socket.close()

bot=ClientNODERB("learnbot1") #nombre del bot en la name no el fichero json
print "Bot adquirido."
cam=threading.Thread(target=run_camera,args=(bot.camera,))
cam.setDaemon(True)
cam.start()

time.sleep(2)

while True:
    time.sleep(0.05)
