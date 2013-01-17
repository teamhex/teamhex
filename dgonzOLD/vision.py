"""
MASLAB Vision processing module
Team Hex
January 2013
"""
xRes = 340
yRes = 240
thetaViewX = math.radians(60)
thetaViewY = math.radians(90)
thetaCam = math.radians(45)
hCam = 5.0
rBall = 1.125

def calcY(py):
    phi= math.atan(py/((yRes/2.0)/math.tan(thetaViewY/2.0)))
    d = (hCam- rBall)/math.tan(thetaCam - phi)
    return d

def calcX(px,y):
    return  px/((xRes/2.0)/math.tan(thetaViewX/2.0))*y

def getBallCoords(px,py,pose):
    ballRelY = calcY(py)
    ballRelX = calcX(px, ballRelY)
    r = math.sqrt(ballRelX**2+ballRelY**2)
    theta = math.atan2(ballRelY,ballRelX)-math.pi/2.0
    x = pose[0]+r*math.cos(pose[2]+theta)
    y = pose[1]+r*math.sin(pose[2]+theta)
    return [x,y]
