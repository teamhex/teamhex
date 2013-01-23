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

def update(stop = False, rotate=False):
    global pose,sensorPoints

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])

    #print data, pose
    #-------------------------Update Sensor Values

    sensorPoints = sensor.update(data[2:7],pose)

    #-------------------------Debug Print

    [forSet,angSet] = waypointNav.update(pose)
    if abs(angSet) > 3.5:
        angSet = 3.5*abs(angSet)/angSet
    if abs(forSet) > 3.5:
        forSet = 3.5*abs(forSet)/forSet

    if rotate:
        mot.setAngForVels(0,3.5)
    else:
        mot.setAngForVels(forSet,angSet)
    #mot.setAngForVels(.5,0)

    [dThetaLdt,dThetaRdt] = odo.getVel()
    [lCommand,rCommand] = mot.update(dThetaLdt,dThetaRdt)

    if debug:
        print pose,sensorPoints

    if(stop):
        ser.sendCommand(mot.getMotorCommandBytes(0,0))
    else:
        ser.sendCommand(mot.getMotorCommandBytes(lCommand,rCommand))

def cleanQuit(signal, frame):
    global pose
    print "Interrupt received"
    #pygame.quit()
    update(True)
    print pose
    ser.serMot.stop()
    ser.serEnc.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def rotate():
    print 'Here'
    ROTATE_TIME = 5
    start = time.time()
    while time.time() < start+ROTATE_TIME:
        update(stop=False,rotate=True)
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for sen in sensorPoints:
            if(sen[2]):
                myMap.wallDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
            else:
                myMap.wallNotDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))

def goMap():
    global myMap
    myMap.initMapping()

    initialize()

    pygame.init()
    fpsClock = pygame.time.Clock()

    width,height = 900,900
    main_surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Robot location and vision')

    RED_COLOR = pygame.Color(255,0,0)
    WHITE_COLOR = pygame.Color(255,255,255)
    BLACK_COLOR = pygame.Color(0,0,0)
    BLUE_COLOR = pygame.Color(0,0,255)

    realHeight,realWidth = 900,900

    ROBOT_RADIUS = 7

    p = CPosition()

    q = False
    i = 0
    waypointNav.addWaypoint([450,450,0,False])
    while not q:
        update()
        #print waypointNav.wp
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for sen in sensorPoints:
            if(sen[2]):
                myMap.wallDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
            else:
                myMap.wallNotDetected(ctypes.c_double(sen[0]), ctypes.c_double(sen[1]))
        if len(waypointNav.wp) == 0:
            rotate()
            myMap.setConfigSpace()
            myMap.closestUnvisited(ctypes.byref(p))
            myMap.goPlan(ctypes.c_double(p.x), ctypes.c_double(p.y))
            waypoints = []
            for j in xrange(myMap.getPlanLength()):
                myMap.getPlanWP(j,ctypes.byref(p))
                waypoints.append([p.x,p.y,0,False])
            print waypoints
            waypointNav.addWaypoints(waypoints)
        mw,mh = main_surface.get_size()
        main_surface.fill(WHITE_COLOR)
        myMap.setConfigSpace()
        for x in xrange(realHeight):
            for y in xrange(realWidth):
                if(myMap.getWall(x,y)):
                    pygame.draw.rect(main_surface,BLACK_COLOR,(x,(realHeight-y),3,3))

        pygame.draw.circle(main_surface, BLUE_COLOR, (int(pose[0]),(realHeight-int(pose[1]))), ROBOT_RADIUS, 3)
        print "Here"
        for s in sensorPoints:
            if(s[2]):
                color = RED_COLOR
            else:
                color = BLACK_COLOR
            pygame.draw.line(main_surface, color, (int(pose[0]),(realHeight-int(pose[1]))), (int(s[0]),(realHeight-int(s[1]))), 3)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                q = True
        if not q:
            pygame.display.update()
        fpsClock.tick(120)
    cleanQuit('','')

goMap()
