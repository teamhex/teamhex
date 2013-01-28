import ctypes
import math
import os

path = os.path.dirname(os.path.realpath(__file__))
myCam = ctypes.CDLL(path+"/../vision/_vision.so")

WIDTH = 320
HEIGHT = 240

# Ball localization, using center point
camAngle = math.pi/2.0 # might change
sinCamAngle = math.sin(camAngle)
cosCamAngle = math.cos(camAngle)
camHeight = 5 # might change
ballHeight = 2.5 # fixed by the contest rules
focalLengthX = 277 # calibrate please (maybe correct?)
focalLengthY = 120

# dX and dY are the displacement of the center of the blob, relative to the image's center.
# Based on that and the height and width of the picture,
#   the angles of the ball relative to the camera's center can be calculated.
# With those angles and information about the balls size, camera's location and focalLength,
#   we can estimate the ball's location.
# dX should be positive if the pixel is at the right and negative otherwise.
# dY should be positive if the pixel is above and negative otherwise.
# We make the following assumptions:
#   Playing field is flat;
#   camAngle is relative to the playing field;
#   camHeight is relative to the field;
#   dX and dY describe the position of the center of the ball seen on screen.
# Note on pose: y is pointing in the same direction as the robot, x is perpendicular and pointing to the left.
def getRelativeBallPose(dX,dY):
    global sinCamAngle,cosCamAngle,camHeight,ballHeight,focalLengthX,focalLengthY
    a = (2.0*cam - ball)/2.0
    y = a*(sinCamAngle*dY + cosCamAngle*focalLengthX)/(sinCamAngle*focalLengthX - cosCamAngle*dY)
    x = focalLengthY/(dY * math.sqrt(x**2 + cam**2))
    return (x,y)
