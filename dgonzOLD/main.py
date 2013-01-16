"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import motorControl as mot
import serialComm as ser
import waypointNav
import odo
import math

debug = True

pose = [0,0,0]

def initialize():
    ser.initialize(encPort = '/dev/arduino_encoders',motPort = '/dev/arduino_control', myBaud = 1000000)
    #waypointNav.initialize()
    ser.sendCommand(mot.getMotorCommandBytes(0,0))
    
def update():
    global pose
    
    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receive()
    
    #print data
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])
    
    if((pose != odo.pose) and debug):
        print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))
    
    #-------------------------Update Waypoint Navigator
    
    #[forSet,angSet] = waypointNav.update(pose)
    #mot.setAngForVels(forSet,angSet)
    
    #-------------------------Update Motor Controller
    [dThetaLdt, dThetaRdt] = odo.getVel()
    
    [lCommand, rCommand] = mot.update(dThetaLdt, dThetaRdt)
    ser.sendCommand(mot.getMotorCommandBytes(lCommand,rCommand))

def testVel():
    initialize()
    i = 0
    mot.setForVel(0)
    while(True):
        i+=1
        if (i/500.0== 1):
            print "lol"
            mot.setForVel(2)
        elif(i/1000.0 == 1):
            print "lol2"
            mot.setForVel(-2)
        elif(i/1500.0 == 1):
            print "lol3"
            mot.setForVel(0)
            mot.setAngVel(.5)
        elif(i/2000.0 == 1):
            print "lol4"
            mot.setAngVel(-.5)
        elif(i/2500.0 == 1):
            print "lol5"
            i = 0
            mot.setAngForVels(0,0)
        update()
        
def testWaypoints():
    initialize()
    waypointNav.addWaypoints([[24,0,0],[24,24,math.pi/2.0],[0,24,math.pi],[0,0,0]])
    while(True):
        update()

testVel()
