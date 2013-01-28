"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import motorControl as mot
import serialComm as ser
import odo as odo
import distanceSensors as sen
import waypointNav as wpNav

import multiprocessing as mp
import math
import time

MAX_FOR_SPEED = 6.0
MAX_ANG_SPEED = 6.0
debug = False

WAYPOINT = 0
BASIC = 1
CONTROLLER = mp.Value('i', BASIC)

basicFor = mp.Value('d', 0.0)
basicAng = mp.Value('d', 0.0)

# WPNav communication memory
commandQueue = mp.Queue()
# Commands:
ACTIVATE = 0
DEACTIVATE = 1
CLEAR = 2
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
realWidth = 150
realHeight = 150

inWait = mp.Value('i',1)

def initialize():
    ser.initialize()
    wpNav.initialize()
    odo.initialize(realWidth/2.0, realHeight/2.0)
    
    wpNav.clearWaypoints()
    wpNav.deactivate()
    CONTROLLER.value = BASIC
    basicFor.value = basicAng.value = 0.0
    stopCommand.value = 0
    inWait.value = 1

    p = mp.Process(target=controlLoop)
    p.start()

def update(stop = False):
    global pose,sensorData,updateLock,CONTROLLER,basicFor,basicAng

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder,
    #          Sensor 0 (leftmost), Sensor 1, Sensor 2 (center, forward),
    #          Sensor 3, Sensor 4 (rightmost)]
    data = ser.receiveData()

    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])

    #-------------------------Store sensor data
    sensorData = list(data[2:8])

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
    
    #-------------------------Limit speeds according to empirical results
    if abs(forSet) > MAX_FOR_SPEED:
        forSet = math.copysign(MAX_FOR_SPEED,forSet)
    if abs(angSet) > MAX_ANG_SPEED:
        angSet = math.copysign(MAX_ANG_SPEED,angSet)
    mot.setAngForVels(forSet,angSet)

    #-------------------------Use motor controller to get motor commands
    [dThetaLdt,dThetaRdt] = odo.getVel()
    [lCommand,rCommand] = mot.update(dThetaLdt,dThetaRdt)

    #-------------------------Send commands (send STOPS command if update is told to stop)
    if(stop):
        ser.serCont.send('STOPS')
    else:
        ser.sendCommand(mot.getMotorCommandBytes(lCommand,rCommand))

    #-------------------------Debug Print
    if debug:
        print data,pose,sensorData,forSet,angSet,'\n'

def controlLoop(freq=50):
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
        update()
        sharedArray[:] = [pose[0],pose[1],pose[2]] + sensorData
        time.sleep(max(0,1/float(freq) - (time.time()-start)))
    update(stop=True)
    ser.serCont.stop()

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
    commandQueue.put(DEACTIVATE)
    CONTROLLER.value = BASIC
    basicFor.value = forward
    basicAng.value = angular

def setWayPointControl():
    global CONTROLLER
    commandQueue.put(ACTIVATE)
    CONTROLLER.value = WAYPOINT

def addWayPoints(wps):
    inWait.value = 0
    wpQueue.put(wps)

def clearWayPoints():
    inWait.value = 1
    commandQueue.put(CLEAR)

def stop():
    stopCommand.value = 1;
    
def test():
    initialize()
    setWayPointControl()
    addWayPoints([[75+48,75,0,False],[75+24,75,0,False],[75+48,75,0,False],[75,75,0,True]])#[75+5*12,75,0,False]
    raw_input()
    stop()

