"""
Checkpoint 4 teamhex
MASLAB 2013
dgonz@mit.edu
"""

import os
import serial
import time
from pylib.PIDControlModule import PIDController
import vision.vision as vision

class Serial:
    def __init__(self, baudrate=115200, prestring='/dev/ttyACM'):
        self.baudrate = baudrate
        self.prestring = prestring
        self.connection = None

    def connect(self, port = None):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if port == None:
            for i in range(0,10):
                port = self.prestring+str(i)
                if os.path.exists(self.prestring+str(i)):
                    break
        self.connection = serial.Serial(port)
        self.connection.baudrate = self.baudrate
        self.connection.rtscts = True

    def send(self, msg):
        try:
            print "Sending"
            self.connection.write('S' + str(msg) + 'E')
            self.connection.flushOutput()
            print 'S' + str(msg) + 'E'
        except:
            time.sleep(2)
            self.connect()
            self.send(msg)

    def receive(self, size=1):
        while True:
            while self.connection.read() != 'S':
                pass
            buf = ''
            for i in xrange(size):
                buf = buf+self.connection.read()
            if self.connection.read() == 'E':
                return buf

    def stop(self):
        self.connection.close()

robot = Serial()
robot.connect()

ZERO = 127
def goForward():
    robot.send( chr(ZERO+70) + chr(ZERO+70))
def goBack():
    robot.send( chr(ZERO-70) + chr(ZERO-70))
def stop():
    robot.send( chr(ZERO) + chr(ZERO))
def turnLeft():
    robot.send( chr(ZERO+50) + chr(ZERO-50))
def turnRight():
    robot.send( chr(ZERO-50) + chr(ZERO+50))
def disconnect():
    robot.stop()

def limitCommand(var,minVal, maxVal):
    if var>maxVal:
        var = maxVal
    elif var<minVal:
        var = minVal
    return var
    
def motCmdBytes(x):
    #Converts an input into two bytes to be sent to the Arduino
    #input commands can be from [-255 : 255]
    x = limitCommand(int(x),-255,255)
    if x>=0:
        return chr(0)+chr(x)
    elif x<0:
        return chr(abs(x))+chr(0)

def commandMotors(lPWM,rPWM):
    #send a command to motors. Commands can range from -255 to 255
    sendIt = motCmdBytes(lPWM)+motCmdBytes(rPWM)
    robot.send(sendIt)

def getBallPose():
    #TODO: implement this
    return vision.getBallPose()

def main():
    camRes = [320,240]
    ballPose = [0,0,0] #X, Y, Area
    xTroller = PIDController( mykP = .25, mykI = 0.0005, mykD = 0.001)
    xTroller.setDesired(camRes[0]/2)
    aTroller = PIDController(mykP = .05, mykI = 0.00005, mykD = 0)
    aTroller.setDesired(3600)
    command = 0
    while(True):
        ball = getBallPose()
        xCommand = xTroller.update(ball[0])
        aCommand = aTroller.update(ball[2])
        commandMotors(-1*xCommand+aCommand,xCommand+aCommand)

main()
