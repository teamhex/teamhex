"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import serialComm as ser
import odo as odo
import distanceSensors as sen
import waypointNav as wpNav
import wallFollow as wf

import multiprocessing as mp
import math
import time

MAX_FOR_SPEED = 6.0
MAX_ANG_SPEED = 6.0
debug = False

WAYPOINT = 0
BASIC = 1
WALL_FOLLOW = 2
CONTROLLER = mp.Value('i', WALL_FOLLOW)

basicFor = mp.Value('d', 0.0)
basicAng = mp.Value('d', 0.0)

# WPNav communication memory
commandQueue = mp.Queue()
# Commands:
ACTIVATE = 0
DEACTIVATE = 1
CLEAR = 2
FOLLOW_START = 3
wpQueue = mp.Queue()

pose = [0,0,0]
sensorData = [0.0,0.0,0.0,0.0,0.0]

# Array shared with other processes, format:
# Positions 0,1 and 2 contains respectively: pose x,y,theta
# Positions 3,4,5,6 and 7 contain the 5 sensor values from sensor 0 to sensor 4 respectively.
sharedArray = mp.Array('d',[0]*8)

# Set by other processes to stop this process.
stopCommand = mp.Value('i',0)

# Map specs (important to put the robot in the middle)
realWidth = 450
realHeight = 450

inWait = mp.Value('i',1)
forMove = mp.Value('i',0)

ROBOT_RADIUS = 7.0

def initialize():
    ser.initialize()
    wpNav.initialize()
    wf.initialize()
    odo.initialize(realWidth/2.0, realHeight/2.0)
    
    wpNav.clearWaypoints()
    wpNav.deactivate()
    CONTROLLER.value = WAYPOINT
    basicFor.value = basicAng.value = 0.0
    stopCommand.value = 0
    inWait.value = 1

    p = mp.Process(target=controlLoop)
    p.start()

def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def update(stop = False):
    global pose,sensorData,updateLock,CONTROLLER,basicFor,basicAng

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder,
    #          Sensor 0 (leftmost), Sensor 1, Sensor 2 (center, forward),
    #          Sensor 3, Sensor 4 (rightmost)]
    data = ser.receiveEnc()

    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])

    #-------------------------Store sensor data
    sensorData = ser.receiveSensors(pose)

    sp = getSensorPoints()

    for s in sp[1:4]:
        if distance(pose,s) < ROBOT_RADIUS+3:
            if(wpNav.state == wpNav.TRANSLATING):
                clearWayPoints()
            basicFor.value = 0.0
            if wf.state == wf.FOLLOW:
                wf.reset()

    #-------------------------Get forward and angular velocities
    # Can get them from either a basic (forward,angular) velocity
    # controller, or from a waypoint navigator.
    # Synchronized through locking because modifications will only affect this part
    if(CONTROLLER.value == WAYPOINT):
        [forSet,angSet] = wpNav.update(pose)
        if len(wpNav.wp) == 0:
            inWait.value = 1
        else:
            inWait.value = 0
    elif(CONTROLLER.value == BASIC):
        inWait.value = 1
        [forSet,angSet] = basicFor.value,basicAng.value
    elif(CONTROLLER.value == WALL_FOLLOW):
        [forSet,angSet] = wf.update(sp,pose)

    if forSet == 0:
        forMove.value = 0
    else:
        forMove.value = 1
    
    #-------------------------Limit speeds according to empirical results
    if abs(forSet) > MAX_FOR_SPEED:
        forSet = math.copysign(MAX_FOR_SPEED,forSet)
    if abs(angSet) > MAX_ANG_SPEED:
        angSet = math.copysign(MAX_ANG_SPEED,angSet)
    ser.motSetAngForVels(forSet,angSet)

    #-------------------------Debug Print
    if debug:
        print data,pose,sensorData,forSet,angSet,'\n'

def controlLoop(freq=200):
    global pose,sensorData,stopCommand,sharedArray
    while stopCommand.value == 0:
        start = time.time()
        while not wpQueue.empty():
            wpNav.addWaypoints(wpQueue.get())
        while not commandQueue.empty():
            com = commandQueue.get()
            if(com == ACTIVATE):
                wpNav.activate()
            elif(com == DEACTIVATE):
                wpNav.deactivate()
            elif(com == CLEAR):
                wpNav.clearWaypoints()
            elif(com == FOLLOW_START):
                wf.reset()
        update()
        sharedArray[:] = [pose[0],pose[1],pose[2]] + sensorData
        time.sleep(max(0,1/float(freq) - (time.time()-start)))
    update(stop=True)

def getPose():
    global sharedArray
    return sharedArray[:3]

def getSensorData():
    global sharedArray
    return sharedArray[3:]

def getSensorPoints():
    return sen.update(getSensorData(), getPose())

def setBasicControl(forward=0.0,angular=0.0):
    global CONTROLLER,basicFor,basicAng
    inWait.value = 1
    if forward == 0:
        forMove.value = 0
    else:
        forMove.value = 1
    commandQueue.put(DEACTIVATE)
    CONTROLLER.value = BASIC
    basicFor.value = forward
    basicAng.value = angular

def setWayPointControl():
    global CONTROLLER
    commandQueue.put(ACTIVATE)
    CONTROLLER.value = WAYPOINT

def setWallFollowControl():
    global CONTROLLER
    commandQueue.put(FOLLOW_START)
    CONTROLLER.value = WALL_FOLLOW

def addWayPoints(wps):
    inWait.value = 0
    wpQueue.put(wps)

def clearWayPoints():
    inWait.value = 1
    forMove.value = 0
    commandQueue.put(CLEAR)

def stop():
    stopCommand.value = 1;

def waitingForCommand():
    return inWait.value != 0

def movingForward():
    return forMove.value != 0
    
def test():
    initialize()
    setWayPointControl()
    addWayPoints([[75+48,75,0,False],[75+24,75,0,False],[75+48,75,0,False],[75,75,0,True]])#[75+5*12,75,0,False]
    raw_input()
    stop()

