"""
Wall follower module
MASLAB Team Hex
Rodrigo T. Gomes
rgomes@mit.edu
January 2013
"""

import math
import time

from PIDControlModule import PIDController
import waypointNav as wpNav
import distanceSensors as sen

desiredDist = 10.0

FIND=0
ORIENT=1
FOLLOW=2
LOST_TIMEOUT=3

state=FIND

distAngTroller = PIDController(0.3,0.00,0.3)
lostTimeout = 3 # Tries to move forward for 3 seconds before giving up on recovering the wall

def initialize():
    global state
    print "Wall follower initialized: find wall mode!"
    state=FIND

def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def angDiff(ang1,ang2):
    diff1 = (ang2-ang1)%(2*math.pi)
    diff2 = (ang1-ang2)%(2*math.pi)
    if diff1 < diff2:
        return -diff1
    else:
        return diff2

def update(sensorPoints,pose):
    global state
    global desiredDist
    global timeoutStart,lostTimeout
    
    if state == FIND:
        for i,s in enumerate(sensorPoints[:-1]):
            if s[2] and distance(pose,s) <= desiredDist:
                wpNav.initialize()
                wpNav.clearWaypoints()
                wpNav.addWaypoint([pose[0],pose[1],pose[2]+(sen.angArray[i]-sen.angArray[-1]),True])
                print "Aligning with the wall (using waypoint navigator)"
                state=ORIENT
                return wpNav.update(pose)
        return [6.0,0.0]
    elif state == ORIENT:
        if wpNav.state != wpNav.IDLE:
            return wpNav.update(pose)
        else:
            distAngTroller.setDesired(desiredDist,reset=True)#distance(sensorPoints[0],pose),reset=True)
            print "Found and aligned with wall, following now."
            state = FOLLOW
            return [0,0]
    elif state == FOLLOW:
        sp = sensorPoints
        if not sp[-1][2] and not sp[-2][2]:
            print "Lost wall, trying to find it again."
            timeoutStart = time.time()
            state = LOST_TIMEOUT
            return [6.0,-2.0]
        elif not sp[-2][2]:
            dist = distance(sp[-1],pose)
        elif not sp[-1][2]:
            dist = distance(sp[-2],pose)
        else:
            ax,ay = sp[-2][0]-sp[-1][0],sp[-2][1]-sp[-1][1]
            bx,by = pose[0]-sp[-1][0],pose[1]-sp[-1][1]
            x = distance(pose,sp[-1])
            dist = x*math.sqrt(1- (ax*bx + ay*by)/(distance(sp[-1],sp[-2])*x))
        return [6.0,distAngTroller.update(dist)]
    elif state == LOST_TIMEOUT:
        if sensorPoints[-1][2] or sensorPoints[-2][2]:
            print "Found wall again, back to following it."
            distAngTroller.setDesired(desiredDist,reset=True)
            state = FOLLOW
            return [0,0]
        elif (time.time()-timeoutStart) > lostTimeout:
            state=FIND
        return [6.0,-2.0]


def reset():
    global state
    initialize()
