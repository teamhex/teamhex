"""
MASLAB Motor Control Module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""

from lib.PIDControlModule import PIDController
import math
import time

#Wheel velocities in [rad/second]
lVel = 0 
rVel = 0 
dt = 0
tPrev = 0

forVel = 0
angVel = 0

kV = 340.32 #Motor voltage constant [RPM/Volt]
vMax = 12.0 #Maximum motor voltage [volts]
b = 6 #Wheel Base (measured from wheel to center point) [inches]
kG = 13.5 #Gear Ratio
dWheel = 3.8625 #Wheel diameter [inches]
maxAngVel = kV*vMax/60.0*kG*2.0*math.pi #Max Wheel Angular Velocity in RPM

#PI Velocity controllers

conv=256/(vMax*kV)*(60)/(2*math.pi) #[PWM/(rad/s)]
kP = conv*27.5
kI = .1*kP
kD = 0
lVelTroller = PIDController(kP, kI, kD)
rVelTroller = PIDController(kP, kI, kD)
balanceTroller = PIDController(mykP = .00, mykI = 0, mykD = 0)

def limitAngVel(a):
    if a>maxAngVel:
        a = maxAngVel
    elif a<(-1*maxAngVel):
        a = -1*maxAngVel
    return a

def setVels(vL = 0, vR = 0):
    lVelTroller.setDesired(limitAngVel(vL))
    rVelTroller.setDesired(limitAngVel(vR))
    balanceTroller.setDesired(rVelTroller.getDesired()-lVelTroller.getDesired())
    
def limitCommand(var,minVal, maxVal):
    if var>maxVal:
        var = maxVal
    elif var<minVal:
        var = minVal
    return var

def setAngForVels(forVelNew,angVelNew):
    global forVel
    global angVel 
    forVel = forVelNew*2.0/dWheel
    angVel = angVelNew*2.0/dWheel*b
    setVels(forVelNew-angVelNew,forVelNew+angVelNew)

def setForVel(x):
    global angVel
    setAngForVels(x,angVel)
    
def setAngVel(x):
    global forVel
    setAngForVels(forVel,x)
    
def motCmdBytes(x):
    #Converts an input into two bytes to be sent to the Arduino
    #input commands can be from [-255 : 255]
    x = limitCommand(int(x),-255,255)
    if x>=0:
        return chr(0)+chr(x)
    elif x<0:
        return chr(abs(x))+chr(0)

def getMotorCommandBytes(lPWM,rPWM):
    #send a command to motors. Commands can range from -255 to 255
    return motCmdBytes(lPWM)+motCmdBytes(rPWM)
    
def update(lVel, rVel):
    bal = balanceTroller.update(rVel-lVel)
    lCommand = lVelTroller.update(lVel)-bal
    rCommand = rVelTroller.update(rVel)+bal
    return [lCommand, rCommand]
