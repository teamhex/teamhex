"""
MASLAB Odometry Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import math
import time

diff = 1000

thetaL = 0
thetaR = 0
dThetaL = 0
dThetaR = 0
dThetaLdt = 0
dThetaRdt = 0
x = 75
y = 75
theta = 0
pose = [x,y,theta]

b = 6 #Wheel Base (measured from wheel to center point) [inches]
rWheel = 3.8625/2.0 #Wheel radius [inches]
cpr = 1000.0 #[Encoder counts per revolution]
kG = 13.5#Gear Ratio

#Previous timestep encoder values
lEncPrev = 0
rEncPrev = 0

tPrev = 0

#note, a positive change in wheel angle signifies thr robot moving forward, for BOTH wheels. 

def fixAngle(ang):
    ang = ang%(math.pi*2.0)
    return ang

#Call every timestep
def update(lEnc, rEnc):
    global lEncPrev
    global rEncPrev
    global x
    global y
    global theta
    global pose
    global dThetaL
    global dThetaR
    global dThetaLdt
    global dThetaRdt
    global thetaL
    global thetaR
    global tPrev
    
    #if((lEnc-lEncPrev)>diff or (rEnc-rEncPrev)>diff):
    #   
    #    lEnc = lEncPrev
    #    rEnc = rEncPrev
    
    dt = time.time()-tPrev #In order to normalize the velocity with respect to time.
    dThetaL = float(lEnc-lEncPrev)/cpr/kG*2*math.pi
    dThetaR = float(rEnc-rEncPrev)/cpr/kG*2*math.pi
    dThetaLdt = dThetaL/dt
    dThetaRdt = dThetaR/dt
    thetaL = float(lEnc)/cpr/kG*2*math.pi
    thetaR = float(rEnc)/cpr/kG*2*math.pi
    
    #Update the angle 
    """
    #Done by integrating the change in angle every timestep
    theta = theta + (rWheel/(2*b))(dThetaR-dThetaL)
    """
    #Done by using the current wheel angle values
    theta = fixAngle((rWheel/(2*b))*(thetaR-thetaL))
    
    #Update X and Y
    x = x+(rWheel/2.0)*(dThetaR+dThetaL)*math.cos(theta)
    y = y+(rWheel/2.0)*(dThetaR+dThetaL)*math.sin(theta)
    
    pose = [x,y,theta]
    
    lEncPrev = lEnc
    rEncPrev = rEnc
    
    tPrev = time.time()
    return pose

def getVel():
    global dThetaLdt
    global dThetaRdt
    return [dThetaLdt, dThetaRdt]
