import os
import time
import ctypes
import math
import multiprocessing as mp

# Hue parameters
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
PURPLE = (160,32,240)

hues = [
    (125,35,GREEN),
    (0,20,RED),
    (55,10,YELLOW),
    (255,10,PURPLE)
    ]

ballHues = set([
        GREEN,
        RED
        ])

def hueDiff(ang1,ang2):
    return min((ang2-ang1)%360, (ang1-ang2)%360)

def getHue(area):
    global hues
    areaHue = (area.pixel>>16)
    for h in hues:
        if hueDiff(areaHue, h[0]) <= h[1]:
            return h[2]
    return None

# Initialize the ctypes stuff
path = os.path.dirname(os.path.realpath(__file__))
myCam = ctypes.CDLL(path+'/_vision.so')

class CPixelArea(ctypes.Structure):
    _fields_ = [('pixel', (ctypes.c_int)),
                ('centerL', (ctypes.c_int)),
                ('centerC', (ctypes.c_int)),
                ('topLeftL', (ctypes.c_int)),
                ('topLeftC', (ctypes.c_int)),
                ('bottomRightL', (ctypes.c_int)),
                ('bottomRightC', (ctypes.c_int)),
                ('size', (ctypes.c_int))]

# Functions for calculating a ball position, given its area
# Camera specs
xRes = 320
yRes = 240
thetaViewX = math.radians(60)
thetaViewY = math.radians(90)
focalY = (yRes/2.0)/math.tan(thetaViewY/2.0)
focalX = (xRes/2.0)/math.tan(thetaViewX/2.0)
thetaCam = math.radians(20)
hCam = 4.25
MAX_RELIABLE_PHI = 0.034 # Empirically calibrated for 16" away from robot's center

# Game Specs
rBall = 1.125
robotRadius = 7.0

def calcY(py):
    phi= math.atan(py/focalY)
    if phi > MAX_RELIABLE_PHI:
        return None
    d = (hCam- rBall)/math.tan(thetaCam - phi)
    return d

def calcX(px,y):
    return  px/focalX*math.sqrt(y**2+hCam**2)

def getBallCoords(area,pose):
    px = area.centerC-xRes/2.0
    py = yRes/2.0-area.centerL

    width = area.topLeftC-area.bottomRightC
    # Formula from excel:
    if 36 <= width <= 115:
        ballRelY = 0.00225*width**2 - 0.50065*width + 32.708
    else:
        ballRelY = None
    #ballRelY = calcY(py)
    if ballRelY is None:
        return None
    ballRelX = calcX(px, ballRelY)
    ballRelY = ballRelY + robotRadius
    r = math.sqrt(ballRelX**2+ballRelY**2)
    theta = math.atan2(ballRelY,ballRelX)-math.pi/2.0
    x = pose[0]+r*math.cos(pose[2]+theta)
    y = pose[1]+r*math.sin(pose[2]+theta)
    return [x,y]

# Concurrency variables:
#  Stop parameter
#  Array of detected areas
stopCommand = mp.Value('i',0)
nAreas = mp.Value('i',0)
areas = mp.Array(CPixelArea, xRes*yRes)
cameraDevice = '/dev/video1'

def initialize(camDevice = '/dev/video1'):
    global cameraDevice
    cameraDevice = camDevice

    stopCommand.value = 0
    nAreas.value = 0

    p = mp.Process(target=camLoop)
    p.start()

def stop():
    stopCommand.value = 1

def camLoop(freq=10):
    global myCam,cameraDevice,stopCommand,nAreas,areas
    myCam.startCam(cameraDevice)
    myCam.enableCam()
    while stopCommand.value == 0:
        start = time.time()
        goPicture()
        nAreas.value = myCam.getNAreas()
        for i in xrange(nAreas.value):
            myCam.getArea(i, ctypes.byref(areas[i]))
        time.sleep(max(0,1/float(freq) - (time.time()-start)))
    myCam.stopCam()
        

# Functions for taking a picture and processing it.
def goPicture():
    myCam.setPicture()
    myCam.getInfo()

def copyCPixelArea(originalArea):
    newArea = CPixelArea()
    newArea.topLeftL = originalArea.topLeftL
    newArea.topLeftC = originalArea.topLeftC
    newArea.bottomRightL = originalArea.bottomRightL
    newArea.bottomRightC = originalArea.bottomRightC
    newArea.pixel = originalArea.pixel
    newArea.centerL = originalArea.centerL
    newArea.centerC = originalArea.centerC
    newArea.size = originalArea.size
    return newArea

def getAreas():
    return [copyCPixelArea(a) for a in areas[:nAreas.value]]

def isBall(area):
    return (getHue(area) in ballHues)

def getAreaAngle(area,pose):
    theta = math.atan((area.centerC-xRes/2.0)/focalX)
    return (pose[2]-theta)%(2*math.pi)
