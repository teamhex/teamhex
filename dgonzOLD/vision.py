"""
MASLAB Vision processing module
Team Hex
January 2013
"""
xRes = 340
yRes = 240
thetaViewX = math.radians(60)
thetaViewY = math.radians(90)
focalY = (yRes/2.0)/math.tan(thetaViewY/2.0)
focalX = (xRes/2.0)/math.tan(thetaViewX/2.0)
thetaCam = math.radians(45)
hCam = 5.0
rBall = 1.125

robotRadius = 7

def calcY(py):
    phi= math.atan(py/focalY)
    d = (hCam- rBall)/math.tan(thetaCam - phi)
    return d

def calcX(px,y):
    return  px/focalX*math.sqrt(y**2+hCam**2)

def getBallCoords(px,py,pose):
    ballRelY = calcY(py)
    ballRelX = calcX(px, ballRelY)
    ballRelY = ballRelY + robotRadius
    r = math.sqrt(ballRelX**2+ballRelY**2)
    theta = math.atan2(ballRelY,ballRelX)-math.pi/2.0
    x = pose[0]+r*math.cos(pose[2]+theta)
    y = pose[1]+r*math.sin(pose[2]+theta)
    return [x,y]
