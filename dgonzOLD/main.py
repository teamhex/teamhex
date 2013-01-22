"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import signal
import sys
import motorControl as mot
import serialComm as ser
import waypointNav
import odo
import math
import time
import sensor
import random

debug = False

pose = [0,0,0]

def initialize():
    ser.initialize(encPort = '/dev/arduino_encoders',motPort = '/dev/arduino_control', myBaud = 1000000)
    waypointNav.initialize()
    ser.sendCommand(mot.getMotorCommandBytes(0,0))

prevData = None,None
def weird(data):
    global prevData
    epsilon = 25000
    pe1,pe2 = prevData
    e1,e2 = data
    if pe1 is None or pe2 is None:
        prevData = e1,e2
        return False
    elif abs(pe1-e1) > epsilon or abs(pe2-e2) > epsilon:
        return True
    else:
        prevData = e1,e2
        return False

def update():
    global pose

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    print data
    #if(weird(data)):
    #    return
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])
    
    #-------------------------Update Sensor Values
    sensorPoints = sensor.update(data[2:7],pose)
    
    #-------------------------Debug Print
    if debug:
        print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))

    #-------------------------Update Waypoint Navigator

    [forSet,angSet] = waypointNav.update(pose)
    if(forSet>3.5):
        forSet = 3.5
    if(angSet>3.5):
        angSet = 3.5
    elif(angSet<-3.5):
        angSet = -3.5
    mot.setAngForVels(forSet,angSet)
    #print [forSet,angSet]
    

    #-------------------------Update Motor Controller
    [dThetaLdt, dThetaRdt] = odo.getVel()

    [lCommand, rCommand] = mot.update(dThetaLdt, dThetaRdt)
    #print lCommand,rCommand
    ser.sendCommand(mot.getMotorCommandBytes(lCommand,rCommand))

def testVel():
    initialize()
    i = 0
    while(True):
    #    i+=1
    #    if (i/500.0== 1):
    #        print "lol"
    #        mot.setForVel(2)
    #    elif(i/1000.0 == 1):
    #        print "lol2"
    #        mot.setForVel(-2)
    #    elif(i/1500.0 == 1):
    #        print "lol3"
    #        mot.setForVel(0)
    #        mot.setAngVel(1)
    #    elif(i/2000.0 == 1):
    #        print "lol4"
    #        mot.setAngVel(-1)
    #    elif(i/2500.0 == 1):
    #        print "lol5"
    #        i = 0
    #        mot.setAngForVels(0,0)
        update()

def testWaypoints():
    initialize()
    waypointNav.addWaypoints([[36,0,0,False],[36,36,0,False],[76,0,0,False],[-36,-36,0,False],[0,0,0,False],[3,0,0,False]])
    t0 = time.time()
    while(True):
        update()
        if(len(waypointNav.wp)==0):
            print "Runtime: "+str(time.time()-t0)
            cleanQuit('','')
            #waypointNav.addWaypoints([[24,0,0],[24,24,math.pi/2.0],[0,24,math.pi],[0,0,0]])

def cleanQuit(signal, frame):
    print "Interrupt received"
    ser.sendCommand(mot.getMotorCommandBytes(0,0))
    ser.serEnc.stop()
    ser.serMot.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

def goMock():
    initialize()
    while True:
        if(len(wayPointNav.wp)):
            x = random.randrange(-240,240)
            y = random.randrange(-240,240)
            wayPointNav.addWaypoints([[x,y,0]])
        update()
        

testWaypoints()
