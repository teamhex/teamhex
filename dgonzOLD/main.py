"""
MASLAB Main Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import motorControl as mot
import serialComm as ser
import odo
import math

debug = True

pose = [0,0,0]


serPort = "/dev/ttyACM0"
serBaud = 1000000


def initialize():
    ser.initialize(serPort, serBaud)

def update():
    global pose
    
    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receive()
    
    #-------------------------Update Odometry
    odo.update(data[0],data[1])
    if(pose != odo.pose && debug):
        pose = odo.pose
        print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))
    
    #-------------------------Update Motor Controller
    [dThetaL, dThetaR] = odo.getVel()
    #Make sure gear ratio is taken into account
    [lCommand, rCommand] = mot.update(dThetaL, dThetaR)

def main():
    initialize()
    while(True):
        update()
        
main()
