"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import signal
import sys
import math
import ctypes
import os
import time

import dgonzOLD.motorControl as mot
import dgonzOLD.serialComm as ser
import dgonzOLD.odo as odo
import dgonzOLD.sensor as sensor

import pygame
from pygame.locals import *

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/mapping/_mapping.so')

class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

debug = True

pose = [0,0,0]
sensorPoints = [(0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False)]

def initialize():
    ser.initialize(contPort = '/dev/arduino_encoders', myBaud = 1000000)

def update(stop = False):
    global pose,sensorPoints

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])

    #-------------------------Update Sensor Values

    sensorPoints = sensor.update(data[2:7],pose)
    
    #-------------------------Debug Print
    if debug:
        print pose,data
        #print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))
    if(stop):
        ser.sendCommand(mot.getMotorCommandBytes(0,0))
    else:
        ser.sendCommand(mot.getMotorCommandBytes(0,0))

def cleanQuit(signal, frame):
    print "Interrupt received"
    pygame.quit()
    update(True)
    ser.serCont.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goMap():
    global myMap
    myMap.initMapping()
    
    initialize()

    realHeight,realWidth = 150,150

    pygame.init()
    fpsClock = pygame.time.Clock()

    width,height = 450,450
    main_surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Robot location and vision')

    ROBOT_RADIUS = 7*3
    RED_COLOR = pygame.Color(255,0,0)
    WHITE_COLOR = pygame.Color(255,255,255)
    BLACK_COLOR = pygame.Color(0,0,0)
    BLUE_COLOR = pygame.Color(0,0,255)

    q = False
    
    while not q:
        update()
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for sen in sensorPoints:
            if(sen[2]):
                myMap.wallDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
            else:
                pass#myMap.wallNotDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
        
        mw,mh = main_surface.get_size()
        main_surface.fill(WHITE_COLOR)
        myMap.setConfigSpace()
        for x in xrange(realHeight):
            for y in xrange(realWidth):
                if(myMap.getWall(x,y)):
                    pygame.draw.rect(main_surface,BLACK_COLOR,(x*3,(realHeight-y)*3,3,3))
        
        pygame.draw.circle(main_surface, BLUE_COLOR, (int(pose[0])*3,(realHeight-int(pose[1]))*3), ROBOT_RADIUS, 1)
        for s in sensorPoints:
            if(s[2]):
                color = RED_COLOR
            else:
                color = BLACK_COLOR
            pygame.draw.line(main_surface, color, (int(pose[0]*3),(realHeight-int(pose[1]))*3), (int(s[0])*3,(realHeight-int(s[1]))*3), 1)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                q = True
        if not q:
            pygame.display.update()
        fpsClock.tick(30)
    cleanQuit('','')

goMap()
