"""
MASLAB Motor Control Module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""

from lib.PIDControlModule import PIDController
import math
import time

#PI Velocity controllers
kP = 1
kI = .1
kD = 0
lVelTroller = PIDController(kP, kI, kD)
rVelTroller = PIDController(kP, kI, kD)

#Wheel velocities in [rad/second]
lVel = 0 
rVel = 0 
dt = 0
tPrev = 0

kV = 340.32 #Motor voltage constant [RPM/Volt]
vMax = 12.0 #Maximum motor voltage [volts]
kG = 1 #Gear Ratio
rWheel = .5 #Wheel radius [meters]
maxAngVel = kV*vMax/60.0*kG*2.0*math.pi #Max Wheel Angular Velocity in RPM

def limitAngVel(a):
    if a>maxAngVel:
        a = maxAngVel
    elif a<(-1*maxAngVel):
        a = -1*maxAngVel
    return a

def commandMotors(vL = 0, vR = 0):
    lVelTroller.setDesired(limitAngVel(vl))
    rVelTroller.setDesired(limitAngVel(vr))
    
def update(dThetaL, dThetaR):
    dt = time.time()-tPrev #In order to normalize the velocity with respect to time. 
    #todo: convert dt to [seconds]
    
    lVel = dThetaL/dt
    rVel = dThetaR/dt
    
    lCommand = lVelTroller.update(lVel)
    rCommand = rVelTroller.update(rVel)
    
    tPrev = time.time()
    return [lCommand, rCommand]
