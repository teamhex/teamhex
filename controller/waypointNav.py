"""
Waypoint navigation module
MASLAB Team Hex
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import math
import time
from PIDControlModule import PIDController

pose = [0,0,0]
desiredPose = None
wp = [] #list of waypoints. One waypoint is of form [x, y, theta] in [inches, inches, radians]

#Finite State Machine Setup
IDLE = 0
ROTATING = 1
DELAY1 = 2
TRANSLATING = 3
DELAY2 = 4
ORIENT = 5
DELAY3 = 6

state = IDLE

active = False
myTimer = 0;

angTroller = PIDController(4.5,0.004,0.005)#.00025,.0.008)
transAngTroller = PIDController(4.5,0.004,0.01)#0.2,.00001,.08)
transTroller = PIDController(.01,.001,.005)

def activate():
    global active
    active = True
    return

def deactivate():
    global wp
    global active
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
    eTheta = 2.0*math.pi/500
    if(abs(angDiff(ang1,ang2))<eTheta):
        return True
    else:
        return False

def compareDist(pose1,pose2):
    eXY = 0.125
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
    global myTimer
    
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
                state = DELAY1
                myTimer = time.time()
                print "WPState = DELAY1"
                transTroller.setDesired(0,reset = True)
                transAngTroller.setDesired(0,reset = True)
                return [0,0]
            else:
                #print "Rotate and pray", pose[2], desiredAngle, angDiff(pose[2],desiredAngle)
                return [0,angTroller.update(angDiff(pose[2],desiredAngle))]
        elif (state == DELAY1):
            if (time.time()-myTimer>=.5):
                state = TRANSLATING
                print "WPState = TRANSLATING"
            return [0,0]
        elif(state == TRANSLATING):
            if(compareDist(pose,desiredPose)):
                state = DELAY2
                print "WPState = DELAY2"
                myTimer = time.time()
                angTroller.setDesired(0,reset = True)
                return [0,0]
            else:
                #Note -dist(vomit) is negative because it is the error (error = desired-actual = 0-dist())
                return [transTroller.update(-dist(pose[0],pose[1],desiredPose[0],desiredPose[1])),transAngTroller.update(angDiff(pose[2],desiredAngle))]
        elif (state == DELAY2):
            if (time.time()-myTimer>=.5):
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
                return [0,0]
        elif(state == ORIENT):
            if(compareAng(pose[2],desiredPose[2])):
                state = DELAY3
                myTimer = time.time()
                print "WPState = DELAY3"
                transTroller.setDesired(0,reset = True)
                transAngTroller.setDesired(0,reset = True)
                return [0,0]
            else:
                return [0,angTroller.update(angDiff(pose[2],desiredPose[2]))]
        elif(state == DELAY3):
            if(time.time()-myTimer>=1):
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
                return [0,0]
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
    state = IDLE
