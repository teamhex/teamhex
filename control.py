"""
MASLAB Robot Simulator
Rodrigo T. Gomes
rgomes@mit.edu
January 2013
"""

import signal
import sys
import os
import ctypes
import time
import math
import threading

import controller.control as ct
import vision.vision as v

import pygame
from pygame.locals import *

import random

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/mapping/_mapping.so')
class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

def cleanQuit(signal, frame):
    print "Interrupt received"
    q = True
    pygame.quit()
    ct.stop()
    v.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goMapping(freq=30):
    global myMap,q

    # Parameters
    RED_BALL = 4
    GREEN_BALL = 5

    myMap.initMapping()
    while not q:
        start = time.time()
        sensorPoints = ct.getSensorPoints()
        pose = ct.getPose()

        areas = [a for a in v.getAreas() if v.getBallCoords(a,pose) is not None]
        # Mapping update
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for a in areas:
            if v.isBall(a):
                coords = v.getBallCoords(a,pose)
                myMap.ballDetected(ctypes.c_double(coords[0]),ctypes.c_double(coords[1]),ctypes.c_int(RED_BALL))
        for s in sensorPoints:
            if(s[2]):
                myMap.wallDetected(ctypes.c_double(s[0]), ctypes.c_double(s[1]))
            else:
                myMap.wallNotDetected(ctypes.c_double(s[0]), ctypes.c_double(s[1]))
        time.sleep(max(0,1.0/float(freq) - (time.time()-start)))

def goPygame():
    global myMap,q
    pygame.init()

    # Parameters
    width,height = 900,900
    realWidth,realHeight = 450,450
    ROBOT_RADIUS = 7
    BALL_RADIUS = 2.5/2.0
    RED_COLOR = pygame.Color(255,0,0)
    GREEN_COLOR = pygame.Color(0,255,0)
    WHITE_COLOR = pygame.Color(255,255,255)
    BLACK_COLOR = pygame.Color(0,0,0)
    BLUE_COLOR = pygame.Color(0,0,255)
    prop = int((width/realWidth + height/realHeight)/2)

    fpsClock = pygame.time.Clock()
    pygame.display.set_caption('Robot location and vision')
    main_surface = pygame.display.set_mode((width, height))
    fieldMap = pygame.transform.scale(
        pygame.image.load("simulator/map.bmp"),
        (width,height))
    main_surface.fill(WHITE_COLOR)
    #main_surface.blit(fieldMap, (0,0))

    while not q:
        pose = ct.getPose()
        sensorPoints = ct.getSensorPoints()
        #main_surface.blit(fieldMap, (0,0))
        main_surface.fill(WHITE_COLOR)

        balls = [v.getBallCoords(a,pose) for a in v.getAreas() if v.getBallCoords(a,pose) is not None]
        for b in balls:
            pygame.draw.circle(main_surface, BLUE_COLOR,
                               (int(b[0])*prop, (realHeight-1-int(b[1]))*prop),
                               int(BALL_RADIUS)*prop, 0)

        pygame.draw.circle(main_surface, BLUE_COLOR,
                           (int(pose[0])*prop,(realHeight-1-int(pose[1]))*prop),
                           ROBOT_RADIUS*prop, prop)
        for s in sensorPoints:
            if(s[2]):
                color = RED_COLOR
            else:
                color = BLACK_COLOR
            pygame.draw.line(main_surface, color,
                             (int(pose[0])*prop,(realHeight-1-int(pose[1]))*prop),
                             (int(s[0])*prop,(realHeight-1-int(s[1]))*prop),
                             prop)
        for x in xrange(realWidth):
            for y in xrange(realHeight):
                if(myMap.getWall(x,y)):
                    pygame.draw.rect(main_surface, RED_COLOR,(x*prop,(realHeight-1-y)*prop,prop,prop))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                q = True
        if not q:
            pygame.display.update()
        fpsClock.tick(50)

def goSim(freq=10.0):
    global myMap,q,mapThread,pygameThread
    q = False

    mapThread = threading.Thread(target=goMapping)
    pygameThread = threading.Thread(target=goPygame)
    
    ct.initialize()
    v.initialize()
    time.sleep(2.0)
    mapThread.start()
    pygameThread.start()

    FOLLOW = 0
    GRAB = 1
    APPROACH_ORIENT = 2
    APPROACH_GO = 3
    state = FOLLOW
    ct.setWallFollowControl()

    while not q:
        start = time.time()
        pose = ct.getPose()
        balls = [x for x in v.getAreas() if v.isBall(x)]
        knownBalls = []
        for b in balls:
            bc = v.getBallCoords(b,pose)
            if bc is not None:
                knownBalls.append(bc)

        
        if state == FOLLOW:
            if len(knownBalls) != 0:
                state = GRAB
                print "Heading to grab ball"
                ct.setWayPointControl()
                ct.addWayPoints([[a[0],a[1],0,False] for a in knownBalls])
            elif len(balls) != 0:
                state = APPROACH_ORIENT
                print "Going towards ball 0"
                ct.setWayPointControl()
                ct.addWayPoints([[pose[0],pose[1],v.getAreaAngle(balls[0],pose),True]])
        elif state == GRAB:
            if ct.waitingForCommand():
                if len(knownBalls) != 0:
                    ct.addWayPoints([[a[0],a[1],0,False] for a in knownBalls])
                else:
                    ct.setWallFollowControl()
                    state = FOLLOW
        elif state == APPROACH_ORIENT:
            if ct.waitingForCommand():
                state = APPROACH_GO
                ct.setBasicControl(forward=6.0)
        elif state == APPROACH_GO:
            if len(knownBalls) != 0:
                state = GRAB
                print "Heading to grab ball"
                ct.setWayPointControl()
                ct.addWayPoints([[a[0],a[1],0,False] for a in knownBalls])
            elif not ct.movingForward():
                state = FOLLOW
                ct.setWallFollowControl()
        time.sleep(max(0,1.0/freq - (time.time()-start)))
    cleanQuit('','')

goSim()
