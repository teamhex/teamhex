import os
from superserial import *
import time

robot = Serial(baudrate=1000000)
robot.connect(port="/dev/arduino_control")


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


ZERO = 0
def goForward():
    commandMotors(70,70)
def goBack():
    commandMotors(-70,-70)
def stop():
    commandMotors(0,0)
def turnLeft():
    commandMotors(-50,50)
def turnRight():
    commandMotors(50,-50)
def disconnect():
    robot.stop()

actions = {
    'f': goForward,
    'b': goBack,
    's': stop,
    'l': turnLeft,
    'r': turnRight,
    }
while True:
    a = raw_input()
    if a in actions:
        actions[a]()
    elif a == 'q':
        stop()
        disconnect()
        break
