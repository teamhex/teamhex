"""
Waypoint navigation module
MASLAB Team Hex
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import math
import time
from lib.PIDControlModule import PIDController

pose = [0,0,0]
desiredPose = None
wp = [] #list of waypoints. One waypoint is of form [x, y, theta] in [inches, inches, radians]

#Finite State Machine Setup
IDLE = 0
ROTATING = 1
TRANSLATING = 2
ORIENT = 3

state = IDLE

active = False

angTroller = PIDController(4.5,0.004,0.005)#.00025,.0.008)
transAngTroller = PIDController(4.5,0.004,0.005)#0.2,.00001,.08)
transTroller = PIDController(.1,.001,.001)

def activate():
    active = True
    return

def deactivate():
    global wp
    wp = []
    active = False
    state = IDLE
    return

def initialize():
    activate()
    print "waypoint Navigator initialized and activated"
    return

def dist(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def getAngle(x1,y1,x2,y2):
    return (math.atan2(y2-y1,x2-x1))%(2*math.pi)

def angDiff(ang1,ang2):
    diff1 = (ang2-ang1)%(2*math.pi)
    diff2 = (ang1-ang2)%(2*math.pi)
    if diff1 < diff2:
        return -diff1
    else:
        return diff2

def compareAng(ang1,ang2):
    #TODO: fix the angles, right now robot will "unwind"
    eTheta = 2.0*math.pi/360.0
    if(abs(angDiff(ang1,ang2))<eTheta):
        return True
    else:
        return False

def compareDist(pose1,pose2):
    eXY = 0.5
    if(dist(pose1[0],pose1[1],pose2[0],pose2[1])<eXY):
        return True
    else:
        return False

def comparePose(pose1, pose2):
    if(compareDist(pose1,pose2) and compareAng(pose1[2],pose2[2])):
        return True
    else:
        return False

def update(myPose):
    """returns a vector [ForwardVel,AngularVel]"""
    global wp
    global pose
    global desiredPose
    global desiredAngle
    global state
    
    if active:
        if(len(wp)!=0):
            desiredPose = wp[0]
        else:
            desiredPose = myPose

        pose = myPose
        desiredAngle = getAngle(pose[0],pose[1],desiredPose[0],desiredPose[1])
                
        if(state == IDLE):
            if(not comparePose(pose,desiredPose)):
                if(compareDist(pose,desiredPose) and desiredPose[3]):
                    state = ORIENT
                    print "WPState = ORIENT"
                    angTroller.setDesired(0,reset = True)
                else:
                    state = ROTATING
                    print "WPState = ROTATE"
                    angTroller.setDesired(0,reset = True)
            elif len(wp) != 0:
                wp.pop(0)
            return [0,0]
        elif(state == ROTATING):
            if(compareAng(pose[2],desiredAngle)):
                state = TRANSLATING
                print "WPState = TRANSLATING"
                transTroller.setDesired(0,reset = True)
                transAngTroller.setDesired(0,reset = True)
                return [0,0]
            else:
                #print "Rotate and pray", pose[2], desiredAngle, angDiff(pose[2],desiredAngle)
                return [0,angTroller.update(angDiff(pose[2],desiredAngle))]
        elif(state == TRANSLATING):
            if(compareDist(pose,desiredPose)):
                if(desiredPose[3] == False):
                    if(len(wp)==0):
                        state= IDLE
                        print "WPState = IDLE"
                        return [0,0]
                    else:
                        wp.pop(0)
                        state = IDLE
                        print "WPState = IDLE"
                        return [0,0]
                else:
                    state = ORIENT
                    print "WPState = ORIENT"
                    angTroller.setDesired(0,reset = True)
                    return [0,0]
            else:
                return [transTroller.update(dist(pose[0],pose[1],desiredPose[0],desiredPose[1])),transAngTroller.update(angDiff(pose[2],desiredAngle))]
        elif(state == ORIENT):
            if(compareAng(pose[2],desiredPose[2])):
                if(len(wp)==0):
                    state= IDLE
                    print "WPState = IDLE"
                    return [0,0]
                else:
                    wp.pop(0)
                    state = IDLE
                    print "WPState = IDLE"
                    return [0,0]
            else:
                return [0,angTroller.update(angDiff(pose[2],desiredPose[2]))]
    else:
        return [0,0]

def addWaypoint(newWP):
    global wp
    wp.append(newWP)

def addWaypoints(newWPs):
    [addWaypoint(x) for x in newWPs]

def clearWaypoints():
    global wp
    wp = []
