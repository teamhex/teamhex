"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import signal
import sys
import time

import simulator.control as ct

import pygame
from pygame.locals import *

import random

def cleanQuit(signal, frame):
    print "Interrupt received"
    pygame.quit()
    ct.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goSim():
    random.seed(time.time())
    
    ct.initialize()
    ct.setWayPointControl()

    pygame.init()
    fpsClock = pygame.time.Clock()

    width,height = 450,450
    main_surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Robot location and vision')

    realWidth,realHeight = 450,450
    ROBOT_RADIUS = 7
    BALL_RADIUS = 2.5/2.0
    RED_COLOR = pygame.Color(255,0,0)
    WHITE_COLOR = pygame.Color(255,255,255)
    BLACK_COLOR = pygame.Color(0,0,0)
    BLUE_COLOR = pygame.Color(0,0,255)

    prop = int((width/realWidth + height/realHeight)/2)
    q = False
    for i in xrange(10):
        wp = [random.randrange(realWidth),random.randrange(realHeight),0,False]
        ct.addWayPoints([wp])
    while not (ct.waitingForCommand() or q):
        sensorPoints = ct.getSensorPoints()
        pose = ct.getPose()
        mw,mh = main_surface.get_size()
        main_surface.fill(WHITE_COLOR)
        pygame.draw.circle(main_surface, BLUE_COLOR,
                           (int(pose[0])*prop,(realHeight-int(pose[1]))*prop),
                           ROBOT_RADIUS*prop, prop)

        for s in sensorPoints:
            if(s[2]):
                color = RED_COLOR
            else:
                color = BLACK_COLOR
            pygame.draw.line(main_surface, color,
                             (int(pose[0])*prop,(realHeight-int(pose[1]))*prop),
                             (int(s[0])*prop,(realHeight-int(s[1]))*prop),
                             prop)
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                q = True
        if not q:
            pygame.display.update()
        fpsClock.tick(60)
    cleanQuit('','')

goSim()
