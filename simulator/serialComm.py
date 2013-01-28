import time
import math

cpr = 200.0
kG = 13.5
dWheel = 3.90625 #Wheel diameter [inches]
b = 5.89 #Wheel Base (measured from wheel to center point) [inches]

lEnc = 0
rEnc = 0

def initialize():
    global lEnc,rEnc,lastUpdate,dThetaLdt,dThetaRdt
    lEnc = 0
    rEnc = 0
    lastUpdate = time.time()
    dThetaLdt = 0
    dThetaRdt = 0

def receiveData():
    global lEnc,rEnc
    update()
    return [lEnc,rEnc,0,0,0,0,0]

def update():
    global lastUpdate,dThetaLdt,dThetaRdt,lEnc,rEnc
    deltaT = time.time()-lastUpdate
    lEnc = lEnc + dThetaLdt*deltaT*cpr*kG/(2*math.pi)
    rEnc = rEnc + dThetaRdt*deltaT*cpr*kG/(2*math.pi)
    lastUpdate = lastUpdate + deltaT

def motSetAngForVels(forward,angular):
    global dThetaLdt,dThetaRdt
    update()
    forward = forward*2.0/dWheel
    angular = angular*2.0/dWheel*b
    dThetaLdt = forward-angular
    dThetaRdt = forward+angular
