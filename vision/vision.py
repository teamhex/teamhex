import ctypes
import time

myCam = ctypes.CDLL('./vision/capture.so')
    
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

#test()
