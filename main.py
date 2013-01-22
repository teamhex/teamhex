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
import dgonzOLD.serialCommOld as ser
import dgonzOLD.odo as odo
import dgonzOLD.sensor as sensor
import dgonzOLD.waypointNav as waypointNav

import pygame
from pygame.locals import *

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/mapping/_mapping.so')

class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

debug = False

pose = [0,0,0]
sensorPoints = [(0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False)]

def initialize():
    ser.initialize()
    waypointNav.initialize()

def update(stop = False):
    global pose,sensorPoints

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    print data
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])

    #-------------------------Update Sensor Values

    sensorPoints = sensor.update(data[2:7],pose)
    
    #-------------------------Debug Print

    [forSet,angSet] = waypointNav.update(pose)
    mot.setAngForVels(fotSet,angSet)

    [dThetaLdt,dThetaRdt] = odo.getVel()
    [lCommand,rCommand] = mot.update(dThetaLdt,dThetaRdt)

    if debug:
        print pose,sensorPoints

    if(stop):
        ser.sendCommand(mot.getMotorCommandBytes(0,0))
    else:
        ser.sendCommand(mot.getMotorCommandButes(lCommand,rCommand))

def cleanQuit(signal, frame):
    print "Interrupt received"
    pygame.quit()
    update(True)
    ser.serMot.stop()
    ser.serEnc.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goMap():
    global myMap
    myMap.initMapping()
    
    initialize()

    realHeight,realWidth = 150,150

    ROBOT_RADIUS = 7

    q = False
    i = 0

    waypointNav.addWaypoints([[-36,0,0,False]])
    while not q:
        update()
        # myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        # for sen in sensorPoints:
        #     if(sen[2]):
        #         myMap.wallDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
        #     else:
        #         myMap.wallNotDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
        # if i == 0:
        #     mw,mh = main_surface.get_size()
        #     main_surface.fill(WHITE_COLOR)
        #     myMap.setConfigSpace()
        #     for x in xrange(realHeight):
        #         for y in xrange(realWidth):
        #             if(myMap.getWall(x,y)):
        #                 pygame.draw.rect(main_surface,BLACK_COLOR,(x*3,(realHeight-y)*3,3,3))
        
        #     pygame.draw.circle(main_surface, BLUE_COLOR, (int(pose[0])*3,(realHeight-int(pose[1]))*3), ROBOT_RADIUS*3, 3)
        #     for s in sensorPoints:
        #         if(s[2]):
        #             color = RED_COLOR
        #         else:
        #             color = BLACK_COLOR
        #         pygame.draw.line(main_surface, color, (int(pose[0])*3,(realHeight-int(pose[1]))*3), (int(s[0])*3,(realHeight-int(s[1]))*3), 3)
        #     for event in pygame.event.get():
        #         if event.type == QUIT:
        #             pygame.quit()
        #             q = True
        #     if not q:
        #         pygame.display.update()
        # i = (i+1)%30
        # fpsClock.tick(120)
    cleanQuit('','')

goMap()
