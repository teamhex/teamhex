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

import simulator.control as ct
import simulator.vision as v

import pygame
from pygame.locals import *

import random

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/mapping/_mapping.so')
class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

NORMAL_WALL = 0
YELLOW_WALL = 1
PURPLE_WALL = 2
BLACK_WALL = 3

def cleanQuit(signal, frame):
    global mapThread,pygameThread,q
    print "Interrupt received"
    q = True
    print recordedBalls
    mapThread.join()
    pygameThread.join()
    pygame.quit()
    ct.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

recordedBalls = set([])

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

        balls = [x for x in v.getAreas(pose) if v.isBall(x)]
        knownBalls = []
        for b in balls:
            bc = v.getBallCoords(b,pose)
            if bc is not None:
                knownBalls.append(bc)

        # Mapping update
        myMap.robotPositioned(ctypes.c_double(pose[0]), ctypes.c_double(pose[1]))
        for a in knownBalls:
            myMap.ballDetected(ctypes.c_double(a[0]),ctypes.c_double(a[1]),ctypes.c_int(RED_BALL))
        for s in sensorPoints:
            if(s[2]):
                myMap.wallDetected(ctypes.c_double(s[0]), ctypes.c_double(s[1]))
            else:
                myMap.wallNotDetected(ctypes.c_double(s[0]), ctypes.c_double(s[1]))
        time.sleep(max(0,1.0/float(freq) - (time.time()-start)))

def goPygame():
    global myMap,q,recordedBalls
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

        #balls = v.getAreas(pose)
        #for b in balls:
        #    pygame.draw.circle(main_surface, BLUE_COLOR,
        #                       (int(b[0])*prop, (realHeight-1-int(b[1]))*prop),
        #                       int(BALL_RADIUS)*prop, 0)

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
                elif(myMap.getBall(x,y)):
                    pygame.draw.circle(main_surface, BLUE_COLOR,
                                       (x*prop, (realHeight-1-y)*prop),
                                       int(BALL_RADIUS)*prop, 0)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                q = True
        if not q:
            pygame.display.update()
        fpsClock.tick(50)

def goSim(freq=50.0):
    global myMap,q,mapThread,pygameThread
    q = False

    mapThread = threading.Thread(target=goMapping)
    pygameThread = threading.Thread(target=goPygame)
    
    ct.initialize()
    v.initialize()
    mapThread.start()
    pygameThread.start()

    FOLLOW = 0
    GRAB = 1
    APPROACH_ORIENT = 2
    APPROACH_GO = 3
    SPIN = 4
    spinDuration = 5.0
    spinStart = time.time()
    state = FOLLOW
    ct.setWallFollowControl()

    startTime = time.time()

    while not q and ((time.time()-startTime) <= 3*60):
        start = time.time()
        pose = ct.getPose()
        myMap.setConfigSpace()
        balls = [x for x in v.getAreas(pose)if v.isBall(x)
                 and canDrive(pose,getPoint(pose,v.getAreaAngle(x,pose),driveDistance))]
        knownBalls = []
        for b in balls:
            bc = v.getBallCoords(b,pose)
            if bc is not None and canDrive(pose, bc):
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
                    ct.setBasicControl(angular=2.0)
                    state = SPIN
                    spinStart = time.time()
                    
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

        elif state == SPIN:
            if len(knownBalls) != 0:
                state = GRAB
                ct.setWayPointControl()
                ct.addWayPoints([[a[0],a[1],0,False] for a in knownBalls])
            elif len(balls) != 0:
                state = APPROACH_ORIENT
                ct.setWayPointControl()
                ct.addWayPoints([[pose[0],pose[1],v.getAreaAngle(balls[0],pose),True]])
            elif time.time()-spinStart >= spinDuration:
                ct.setWallFollowControl()
                state = FOLLOW
                
        time.sleep(max(0,1.0/freq - (time.time()-start)))
    cleanQuit('','')

def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

driveDistance = 16.0

def canDrive(pose, goal):
    x,y = pose[0],pose[1]
    ex,ey = goal
    minDist = (x-ex)**2 + (y-ey)**2
    while True:
        if myMap.getConfigWall(ctypes.c_int(int(x)),ctypes.c_int(int(y))):
            return False
        if (x,y) == goal:
            return True
        neighbors = [
            (x-1,y-1),
            (x-1,y),
            (x-1,y+1),
            (x,y-1),
            (x,y+1),
            (x+1,y-1),
            (x+1,y),
            (x+1,y+1)
            ]
        for (xn,yn) in neighbors:
            dist = (xn-ex)**2 + (yn-ey)**2
            if dist < minDist:
                x,y = xn,yn
                minDist = dist
        if (x,y) not in neighbors:
            return True
    return True

def getPoint(start,orientation,distance):
    x = start[0] + distance * math.cos(orientation)
    y = start[1] + distance * math.sin(orientation)
    return x,y

#goSim()
def start():
    global myMap,q,mapThread,pygameThread
    q = False

    mapThread = threading.Thread(target=goMapping)
    pygameThread = threading.Thread(target=goPygame)
    
    ct.initialize()
    v.initialize()
    mapThread.start()
    pygameThread.start()

    ct.setWallFollowControl()

goSim()
