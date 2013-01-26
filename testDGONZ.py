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

"""
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
"""

debug = False

pose = [0,0,0]
sensorPoints = [(0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False), (0,0,False)]

def initialize():
    ser.initialize()
    odo.initialize(0,0)
    waypointNav.initialize()

def update(stop = False):
    global pose,sensorPoints

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])
    
    """
    #-------------------------Update Sensor Values

    #sensorPoints = sensor.update(data[2:7],pose)
    #print sensorPoints
    
    if waypointNav.state == waypointNav.TRANSLATING:
        for i in sensorPoints[1:6]:
            if ((pose[0]-i[0])**2 + (pose[1]-i[1])**2) < 9.0**2:
                waypointNav.wp = []
                waypointNav.addWaypoint([pose[0],pose[1],pose[2],False])
    """
    #------------------------- Update Waypoint Navigator
    [forSet,angSet] = waypointNav.update(pose)
    
    if abs(forSet) > 3:
        forSet = 3*abs(forSet)/forSet
    if abs(angSet) > 3:
        angSet = 3*abs(angSet)/angSet
    if waypointNav.active:
        mot.setAngForVels(forSet,angSet)
    
    #------------------------- Update Motor Controller
    [dThetaLdt,dThetaRdt] = odo.getVel()
    [lCommand,rCommand] = mot.update(dThetaLdt,dThetaRdt)
    
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


def test():
    initialize()
    waypointNav.addWaypoints([[0,0,math.radians(135),True],[0,0,0,True]])
    while True:
        start = time.time()
        update()
        sleep(max(0, 1.0/50.0 - time.time()-start))
test()
