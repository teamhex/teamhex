"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import lib.superserial as serial
import struct

def initialize(encPort = '/dev/arduino_encoders',motPort = '/dev/arduino_control', myBaud = 115200):
    global serEnc
    global serMot
    serEnc = serial.Serial(myBaud)
    serEnc.connect(port=encPort)
    serMot = serial.Serial(myBaud)
    serMot.connect(port=motPort)
    print "connected!"
    
def sendCommand(command):
    global serMot
    serMot.send(command)
    
def receive():
    global serEnc
    while True:
        data = serEnc.receive()
        if(len(data) == 8):
            return [struct.unpack('>l',data[0:4])[0],struct.unpack('>l',data[4:8])[0]]
