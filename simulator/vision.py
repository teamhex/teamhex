import pygame
import os
import ctypes
import math
from collections import deque

path = os.path.dirname(os.path.realpath(__file__))

thetaViewX = math.radians(60)
detectMin,detectMax = 9.0,16.0
ROBOT_RADIUS = 7.0

BALL_COLOR = (255,0,0)

colors = set([
        BALL_COLOR
        ])

class CPixelArea(ctypes.Structure):
    _fields_ = [('pixel', (ctypes.c_int)),
                ('centerL', (ctypes.c_int)),
                ('centerC', (ctypes.c_int)),
                ('topLeftL', (ctypes.c_int)),
                ('topLeftC', (ctypes.c_int)),
                ('bottomRightL', (ctypes.c_int)),
                ('bottomRightC', (ctypes.c_int)),
                ('size', (ctypes.c_int))]

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

def angDiff(ang1,ang2):
    return min((ang2-ang1)%(2*math.pi), (ang1-ang2)%(2*math.pi))
def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def bfsArea(x,y,color): 
    global fieldMap,visited
    resX,resY = x,y
    size = 1
    q = deque([(x,y)])
    visited[x][y] = True
    while len(q) != 0:
        x,y = q.popleft()
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
        for (x,y) in neighbors:
            if not visited[x][y] and fieldMap.get_at((x,449-y))[:3] == color:
                resX = resX+x
                resY = resY+y
                size = size+1
                visited[x][y] = True
                q.append((x,y))
    resX = float(resX)/float(size)
    resY = float(resY)/float(size)
    return (resX,resY)

def initialize():
    global fieldMap,visited,areas
    areas = []
    fieldMap = pygame.transform.scale(
        pygame.image.load(path+"/map.bmp"),
        (450,450))
    visited = [[False]*450 for i in xrange(450)]
    for x in xrange(450):
        for y in xrange(450):
            if not visited[x][y]:
                color = tuple(fieldMap.get_at((x,449-y))[:3])
                if color in colors:
                    areas.append(bfsArea(x,y, color))
                else:
                    visited[x][y] = True

def getAreas(pose):
    global areas
    retAreas = []
    for i,a in enumerate(areas):
        dist = distance(a,pose)
        if dist <= ROBOT_RADIUS:
            del areas[i]
            continue
        angle = angDiff(math.atan2(a[1]-pose[1],a[0]-pose[0]), pose[2])
        if angle <= thetaViewX/2.0 and (intersect(pose, a) is None):
            retAreas.append(a)
    return retAreas

def getAreaAngle(area,pose):
    return math.atan2(area[1]-pose[1], area[0]-pose[0])

def isBall(area):
    return True

def getBallCoords(area,pose):
    if detectMin <= distance(area,pose) <= detectMax:
        return area
    else:
        return None
