import ctypes
import time
import os

path = os.path.dirname(os.path.realpath(__file__))
myCam = ctypes.CDLL(path+'/_vision.so')

class CPixelArea(ctypes.Structure):
    _fields_ = [('pixel', (ctypes.c_int)),
                ('centerL', (ctypes.c_int)),
                ('centerC', (ctypes.c_int)),
                ('size', (ctypes.c_int))]

def init():
    global myCam
    myCam.startCam("/dev/maslab_camera")
    #myCam.enableCam()

def setSnap(i):
    myCam.setFilePicture("/home/rgomes/Dropbox/snapshots2/snap"+str(i))
    myCam.getInfo()

def nAreas():
    return myCam.getNAreas()

def getArea(i):
    a = CPixelArea()
    myCam.getArea(i, ctypes.byref(a))
    return a
    
def getBallPose():
    global myCam
    myCam.getInfo()
    return [myCam.getX(),60,myCam.getSize()]

def test():
    init()
    start = time.time()
    for i in xrange(3175):
        setSnap(i)
    print time.time()-start


