import ctypes
import time

myCam = ctypes.CDLL('vision/capture.so')
    
def init():
    global myCam
    myCam.startCam("/dev/video7")
    myCam.enableCam()
    print "Calibrating Camera..."
    time.sleep(1)
    
def getBallPose():
    global myCam
    print "before"
    myCam.getInfo()
    print "after"
    return [myCam.getX(),60,myCam.getSize()]

def test():
    init()
    print getBallPose()
    myCam.stopCam()
