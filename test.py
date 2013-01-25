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
import dgonzOLD.waypointNav as waypointNav
import dgonzOLD.vision as vision
import colorsys

import pygame
from pygame.locals import *

import random

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/mapping/_mapping.so')
myCam = ctypes.CDLL(path+'/vision/_vision.so')

class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

class CPixelArea(ctypes.Structure):
    _fields_ = [('pixel', (ctypes.c_int)),
                ('centerL', (ctypes.c_int)),
                ('centerC', (ctypes.c_int)),
                ('size', (ctypes.c_int))]

debug = True

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
    #print pose

    #-------------------------Update Sensor Values

    sensorPoints = sensor.update(data[2:7],pose)
    #print sensorPoints
    if waypointNav.state == waypointNav.TRANSLATING:
        for i in sensorPoints[1:6]:
            if ((pose[0]-i[0])**2 + (pose[1]-i[1])**2) < 9.0**2:
                waypointNav.wp = []
                waypointNav.addWaypoint([pose[0],pose[1],pose[2],False])
    
    #-------------------------Debug Print

    [forSet,angSet] = waypointNav.update(pose)
    if abs(forSet) > 3.5:
        forSet = 3.5*abs(forSet)/forSet
    if abs(angSet) > 3.5:
        angSet = 3.5*abs(angSet)/angSet
    #mot.setAngForVels(forSet,angSet)
    mot.setAngForVels(2.0,0)
    #print forSet,angSet
    #print pose
    #mot.setAngForVels(1,0)
    #mot.setAngForVels(0,0)

    [dThetaLdt,dThetaRdt] = odo.getVel()
    [lCommand,rCommand] = mot.update(dThetaLdt,dThetaRdt)
    #print lCommand,rCommand
    if debug:
        pass#print pose,sensorPoints
        #print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))
    if(stop):
        ser.serCont.send('STOPS')
    else:
        s = mot.getMotorCommandBytes(lCommand,rCommand)
        ser.sendCommand(s)

def cleanQuit(signal, frame):
    print "Interrupt received"
    #pygame.quit()
    update(True)
    ser.serCont.stop()
    #myCam.stopCam()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goMap():
    global myMap
    global myCam
    myMap.initMapping()
    myCam.startCam('/dev/video1')
    myCam.enableCam()
    
    initialize()

    realHeight,realWidth = 150,150

    pygame.init()
    fpsClock = pygame.time.Clock()

    width,height = 450,450
    main_surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Robot location and vision')

    ROBOT_RADIUS = 7
    BALL_RADIUS = 2.5/2.0
    RED_COLOR = pygame.Color(255,0,0)
    WHITE_COLOR = pygame.Color(255,255,255)
    BLACK_COLOR = pygame.Color(0,0,0)
    BLUE_COLOR = pygame.Color(0,0,255)

    xRes,yRes = 320,240

    q = False
    i = 0
    start = time.time()
    while not q and time.time()-start < 60*3:
        update()
        if len(waypointNav.wp) == 0:
            waypointNav.addWaypoints([[random.randrange(30,120), random.randrange(30,120), 0, False]])
        myCam.setPicture()
        myCam.getInfo()
        
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for sen in sensorPoints:
            if(sen[2]):
                myMap.wallDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
            else:
                myMap.wallNotDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
        if i == 0:
            mw,mh = main_surface.get_size()
            main_surface.fill(WHITE_COLOR)
            myMap.setConfigSpace()
            for x in xrange(realHeight):
                for y in xrange(realWidth):
                    if(myMap.getWall(x,y)):
                        pygame.draw.rect(main_surface,BLACK_COLOR,(x*3,(realHeight-y)*3,3,3))
        
            pygame.draw.circle(main_surface, BLUE_COLOR, (int(pose[0])*3,(realHeight-int(pose[1]))*3), ROBOT_RADIUS*3, 3)

            for j in xrange(myCam.getNAreas()):
                a = CPixelArea()
                myCam.getArea(j,ctypes.byref(a))
                x,y = vision.getBallCoords(a.centerC-xRes/2.0, yRes/2.0-a.centerL, pose)
                if(340 < (a.pixel>>16) or 20 > (a.pixel>>16)):
                    c = RED_COLOR
                else:
                    c = BLUE_COLOR
                pygame.draw.circle(main_surface, c, (int(x)*3, int(realHeight-y)*3), int(BALL_RADIUS)*3, 0)
           
            for s in sensorPoints:
                if(s[2]):
                    color = RED_COLOR
                else:
                    color = BLACK_COLOR
                pygame.draw.line(main_surface, color, (int(pose[0])*3,(realHeight-int(pose[1]))*3), (int(s[0])*3,(realHeight-int(s[1]))*3), 3)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    q = True
            if not q:
                pygame.display.update()
        i = 0
        fpsClock.tick(120)
    cleanQuit('','')

goMap()
