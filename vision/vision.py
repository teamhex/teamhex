import ctypes
import time
import os

path = os.path.abspath(__file__)
myCam = ctypes.CDLL(path+'/_vision.so')
    
def init():
    global myCam
    myCam.startCam("/dev/video1")
    myCam.enableCam()
    print "Calibrating Camera..."
    time.sleep(1)
    
def getBallPose():
    global myCam
    myCam.getInfo()
    return [myCam.getX(),60,myCam.getSize()]

def test():
    init()
    for i in xrange(100):
        print getBallPose()
    myCam.stopCam()

test()
