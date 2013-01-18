import signal
import sys
import os
import dgonzOLD.motorControl as mot
import dgonzOLD.serialComm as ser
import dgonzOLD.odo as odo
import math
import time
import dgonzOLD.sensor as sensor
import ctypes

path = os.path.dirname(os.path.realpath(__file__))
myMap = ctypes.CDLL(path+'/_mapping.so')

class CPosition(ctypes.Structure):
    _fields_ = [('x', (ctypes.c_double)),
                ('y', (ctypes.c_double))]

debug = False

pose = [0,0,0]

def initialize():
    ser.initialize(encPort = '/dev/arduino_encoders',motPort = '/dev/arduino_control', myBaud = 1000000)
    ser.sendCommand(mot.getMotorCommandBytes(0,0))

def update():
    global pose

    #-------------------------Receive Data from Arduino
    # data is [Left Encoder, Right Encoder]
    data = ser.receiveData()
    #-------------------------Update Odometry
    pose = odo.update(data[0],data[1])
    
    #-------------------------Update Sensor Values
    sensorPoints = sensor.update(data[2:7],pose)
    
    #-------------------------Debug Print
    if debug:
        print "x = "+str(pose[0])+", y = "+str(pose[1])+", theta = "+str(math.degrees(pose[2]))

def test():
    myMap.initMapping()
    while True:
        update()
        robotPositioned(pose[0], pose[1])
        for i in sensorPoints:
            if(i[2]):
                wallDetected(i[0], i[1])
            else:
                wallNotDetected(i[0], i[1])
        myMap.printCells()

def cleanQuit(signal, frame):
    print "Interrupt received"
    ser.sendCommand(mot.getMotorCommandBytes(0,0))
    ser.serEnc.stop()
    ser.serMot.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

test()
