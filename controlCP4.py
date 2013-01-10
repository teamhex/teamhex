"""
Checkpoint 4 teamhex
MASLAB 2013
dgonz@mit.edu
"""

import os
import serial
import time
from PIDControlModule import PIDController

class Serial:
    def __init__(self, baudrate=115200, prestring='/dev/ttyACM'):
        self.baudrate = baudrate
        self.prestring = prestring
        self.connection = None

    def connect(self, port = '/dev/ttyACM1'):
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

def commandMotors(lPWM,rPWM):
    #send a command to motors. Commands can range from -127 to 127
    lPWM = limitCommand(int(lPWM),-127,127)
    rPWM = limitCommand(int(rPWM),-127,127)
    robot.send(chr(ZERO+lPWM)+chr(ZERO+rPWM))

def getBallPose():
    #TODO: implement this
    return [640,480,300]

def main():
    camRes = [1280,720]
    ballPose = [0,0,0] #X, Y, Area
    xTroller = PIDController(kP = .5, kI = .01, kD = .01)
    xTroller.setDesired(camRes[0]/2)
    command = 0
    while(True):
        command = xTroller.update(getBallPose[0])
        #print command
        commandMotors(-1*command,command)

main()
