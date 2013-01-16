"""
Waypoint navigation module
MASLAB Team Hex
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import math
from lib.PIDControlModule import PIDController

pose = [0,0,0]
desiredPose = [0,0,0]
wp = [] #list of waypoints. One waypoint is of form [x, y, theta] in [inches, inches, radians]

#Finite State Machine Setup
IDLE = 0
ROTATING = 1
TRANSLATING = 2

state = IDLE

angTroller = PIDController(.8,.01,0)
transTroller = PIDController(.8,.01,0)

def initialize():
    print "waypoint Navigator initialized"
    return
    
def dist(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def getAngle(x1,y1,x2,y2):
    return math.atan2(y2-y1,x2-x1)
    
def angDiff(ang1,ang2):
    #TODO: Implement
    diff = ang2-ang1
    return diff
    
def compareAng(ang1,ang2):
    #TODO: fix the angles, right now robot will "unwind"
    eTheta = 2.0*math.pi/500
    if(angDiff(ang1,ang2)<eTheta):
        return True
    else:
        return False

def compareDist(pose1,pose2):
    eXY = .0625
    if(dist(pose1[0],pose1[1],pose2[0],pose2[1])<eXY):
        return True
    else:
        return False
    
def comparePose(pose1, pose2):
    eXY = .0625
    eTheta = 2.0*math.pi/1000
    if(compareDist(pose1,pose2) and compareAng(pose1[2],pose2[2])):
        return True
    else:
        return False
    
def update(myPose):
    """returns a vector [ForwardVel,AngularVel]"""
    global wp
    global pose
    global desiredPose
    global state
    
    pose = myPose
    
    if(state == IDLE):
        print "Sup"
        if(not comparePose(pose,desiredPose)):
            state = ROTATING
            print "WPState = ROTATE"
            angTroller.setDesired(desiredPose[2],reset = True)
        return [0,0]
    elif(state == ROTATING):
        if(compareAng(pose[0],desiredPose[1])):
            state = TRANSLATING
            print "WPState = TRANSLATING"
            transTroller.setDesired(0,reset = True)
            return [0,0]
        else:
            return [0,angTroller.update(pose[2])]
    elif(state == TRANSLATING):
        if(comparePose(pose,desiredPose)):
            if(len(wp)==0):
                state= IDLE
                
                print "WPState = IDLE"
                return [0,0]
            else:
                desiredPose = wp.pop(0)
                state = IDLE
                return [0,0]
        else:
            return [transTroller.update(dist(pose[0],pose[1],desiredPose[0],desiredPose[1])),0]

def addWaypoint(newWP):
    global wp
    wp.append(newWP)
    
def addWaypoints(newWPs):
    [addWaypoint(x) for x in newWPs]
