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
CONTROLLER = BASIC

basicFor = 0
basicAng = 0

pose = [0,0,0]
sensorData = [0.0,0.0,0.0,0.0,0.0]

# Array shared with other processes, format:
# Positions 0,1 and 2 contains respectively: pose x,y,theta
# Positions 3,4,5,6 and 7 contain the 5 sensor values from sensor 0 to sensor 4 respectively.
sharedArray = mp.Array('d',[0]*8)

# Set by other processes to stop this process.
stopCommand = mp.Value('i',0)

updateLock = mp.Lock()

def initialize():
    ser.initialize()
    wpNav.initialize()
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
    updateLock.acquire()
    if(CONTROLLER == WAYPOINT):
        [forSet,angSet] = wpNav.update(pose)
    elif(CONTROLLER == BASIC):
        [forSet,angSet] = basicFor,basicAng
    updateLock.release()
    
    #-------------------------Limit speeds according to empirical results
    if abs(forSet) > MAX_FOR_SPEED:
        forSet = math.copysign(MAX_FOR_SPEED,forSet)
    if abs(angSet) > MAX_ANG_SPEED:
        angSet = mat.copysign(MAX_ANG_SPEED,angSet)
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
    global updateLock,CONTROLLER,basicFor,basicAng
    updateLock.acquire()

    wpNav.deactivate()
    CONTROLLER = BASIC
    basicFor = forward
    basicAng = angular

    updateLock.release()

def setWayPointControl():
    global updateLock,CONTROLLER
    updateLock.acquire()
    
    wpNav.activate()
    CONTROLLER=WAYPOINT

    updateLock.release()

def addWayPoints(wps):
    updateLock.acquire()

    wpNav.addWaypoints(wps)

    updateLock.release()

def clearWayPoints():
    updateLock.acquire()

    wpNav.clearWaypoints()

    updateLock.release()

def stop():
    stopCommand.value = 1;
