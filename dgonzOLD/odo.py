"""
MASLAB Odometry Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import math

thetaL = 0
thetaR = 0
dThetaL = 0
dThetaR = 0
x = 0
y = 0
theta = 0
pose = [x,y,theta]

b = 6 #Wheel Base (measured from wheel to center point) [inches]
rWheel = 3.625 #Wheel radius [inches]
cpr = 4000.0 #[Encoder counts per revolution]

#Previous timestep encoder values
lEncPrev = 0
rEncPrev = 0

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
    global thetaL
    global thetaR
    
    dThetaL = (lEnc-lEncPrev)/cpr*2*math.pi
    dThetaR = (rEnc-rEncPrev)/cpr*2*math.pi
    thetaL = (lEnc)/cpr*2*math.pi
    thetaR = (rEnc)/cpr*2*math.pi
    
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
    
    return pose

def getVel():
    return [dThetaL, dThetaR]
