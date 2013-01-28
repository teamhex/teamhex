import time
import math
import pygame
import os

cpr = 200.0
kG = 13.5
dWheel = 3.90625 #Wheel diameter [inches]
b = 5.89 #Wheel Base (measured from wheel to center point) [inches]

lEnc = 0
rEnc = 0

sensorParams = [
    ( 1794.78516772 , 35.6370381828 ),
    ( 1721.79069881 , 42.4732470183 ),
    ( 1767.11968919 , 25.1189710748 ),
    ( 1779.69282231 , 38.6184904426 ),
    ( 1765.14744502 , 16.9955147657 ),]

# Maybe more?
maxDistance = [30.,23.,30.,18.,20.]
minDistance = [2.5,2.5,2.5,2.5,2.5]
angArray = [math.pi/2.0,math.pi/4.0,0,-math.pi/4.0,-math.pi/2.0]

path = os.path.dirname(os.path.realpath(__file__))

def initialize():
    global lEnc,rEnc,lastUpdate,dThetaLdt,dThetaRdt,fieldMap
    lEnc = 0
    rEnc = 0
    lastUpdate = time.time()
    dThetaLdt = 0
    dThetaRdt = 0
    fieldMap = pygame.transform.scale(
        pygame.image.load(path+"/map.bmp"),
        (450,450))

def receiveEnc():
    global lEnc,rEnc
    update()
    return [lEnc,rEnc]

# Check if line intersects with a wall. Return None if it doesn't, point of intersection if it does.
def intersect(start, end):
    x,y = (int(round(start[0])),int(round(start[1])))
    ex,ey = end
    minDist = (x-ex)**2 + (y-ey)**2
    while True:
        if fieldMap.get_at((x,449-y))[:3] == (0,0,0):
            return (x,y)
        if (x,y) == tuple(end):
            return None
        neighbors = [
            (x-1,y-1),
            (x-1,y),
            (x-1,y+1),
            (x,y-1),
            (x,y+1),
            (x+1,y-1),
            (x+1,y),
            (x+1,y+1)
            ]
        for (xn,yn) in neighbors:
            dist = (xn-ex)**2 + (yn-ey)**2
            if dist < minDist:
                minDist = dist
                x,y = xn,yn
        if (x,y) not in neighbors:
            return None
    return None

def serialLinkTransform(pose,angle,length):
    return [int(round(pose[0]+length*math.cos(pose[2]+angle))),int(round(pose[1]+length*math.sin(pose[2]+angle)))]
    
def receiveSensors(pose):
    res = [45,45,45,45,45]
    for i in xrange(5):
        maxPoint = serialLinkTransform(pose, angArray[i], maxDistance[i]+4.0)
        wall = intersect(pose, maxPoint)
        if wall is not None:
            m,a = sensorParams[i]
            dist = math.sqrt( (wall[0]-pose[0])**2 + (wall[1]-pose[1])**2) - 4.0
            res[i] = float(a) + float(m)/float(dist)
    return res

def update():
    global lastUpdate,dThetaLdt,dThetaRdt,lEnc,rEnc
    deltaT = time.time()-lastUpdate
    lEnc = lEnc + dThetaLdt*deltaT*cpr*kG/(2*math.pi)
    rEnc = rEnc + dThetaRdt*deltaT*cpr*kG/(2*math.pi)
    lastUpdate = time.time()

def motSetAngForVels(forward,angular):
    global dThetaLdt,dThetaRdt
    update()
    forward = forward*2.0/dWheel
    angular = angular*2.0/dWheel*b
    dThetaLdt = forward-angular
    dThetaRdt = forward+angular
