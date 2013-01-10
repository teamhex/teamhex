import ctypes
import time

myCam = ctypes.CDLL('capture.so')
myCam.startCam("/dev/video1")
myCam.enableCam()
print "Calibrating Camera..."
time.sleep(1)
myCam.getInfo()
print myCam.getX()
print myCam.getSize()
myCam.stopCam()

def getBallPose():
    return [320/2,60,3500]
