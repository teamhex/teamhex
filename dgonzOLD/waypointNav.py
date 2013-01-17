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
desiredPose = None
wp = [] #list of waypoints. One waypoint is of form [x, y, theta] in [inches, inches, radians]

#Finite State Machine Setup
IDLE = 0
ROTATING = 1
TRANSLATING = 2

state = IDLE

angTroller = PIDController(2.850,.000875,.0075)
transTroller = PIDController(-.1625,-.000225,-0.005)

def initialize():
    print "waypoint Navigator initialized"
    return

def dist(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def getAngle(x1,y1,x2,y2):
    return math.atan2(y2-y1,x2-x1)

def angDiff(ang1,ang2):
    diff1 = (ang2-ang1)%(2*math.pi)
    diff2 = (ang1-ang2)%(2*math.pi)
    if diff1 < diff2:
        return -diff1
    else:
        return diff2

def compareAng(ang1,ang2):
    #TODO: fix the angles, right now robot will "unwind"
    eTheta = 2.0*math.pi/500.0
    if(abs(angDiff(ang1,ang2))<eTheta):
        return True
    else:
        return False

def compareDist(pose1,pose2):
    eXY = .1875
    if(dist(pose1[0],pose1[1],pose2[0],pose2[1])<eXY):
        return True
    else:
        return False

def comparePose(pose1, pose2):
    if(compareDist(pose1,pose2)):# and compareAng(pose1[2],pose2[2])):
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
    
    if(len(wp)!=0):
        desiredPose = wp[0]

    pose = myPose
    desiredAngle = getAngle(pose[0],pose[1],desiredPose[0],desiredPose[1])
    #print angDiff(pose[2],desiredAngle)

    if(state == IDLE):
        if(not comparePose(pose,desiredPose)):
            state = ROTATING
            print "WPState = ROTATE"
            angTroller.setDesired(0,reset = True)
        return [0,0]
    elif(state == ROTATING):
        if(compareAng(pose[2],desiredAngle)):
            state = TRANSLATING
            print "WPState = TRANSLATING"
            transTroller.setDesired(0,reset = True)
            angTroller.setDesired(0,reset = True)
            return [0,0]
        else:
            return [0,angTroller.update(angDiff(pose[2],desiredAngle))]
    elif(state == TRANSLATING):
        if(comparePose(pose,desiredPose)):
            if(len(wp)==0):
                state= IDLE
                print "WPState = IDLE"
                return [0,0]
            else:
                wp.pop(0)
                state = IDLE
                return [0,0]
        else:
            return [transTroller.update(dist(pose[0],pose[1],desiredPose[0],desiredPose[1])),angTroller.update(angDiff(pose[2],desiredAngle))]

def addWaypoint(newWP):
    global wp
    wp.append(newWP)

def addWaypoints(newWPs):
    [addWaypoint(x) for x in newWPs]
