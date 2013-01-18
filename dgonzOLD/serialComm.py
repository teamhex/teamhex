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
    serEnc = serial.Serial(baudrate=myBaud)
    serEnc.connect(port=encPort)
    serMot = serial.Serial(baudrate=myBaud)
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

def receiveData():
    global serEnc
    while True:
        data = serEnc.receive()
        if(len(data) == 8+5*2):
            return (struct.unpack('>l',data[0:4])[0],struct.unpack('>l',data[4:8])[0],ord(data[8])<<8 | ord(data[9]),ord(data[10])<<8 | ord(data[11]),ord(data[12])<<8 | ord(data[13]),ord(data[14])<<8 | ord(data[15]),ord(data[16])<<8 | ord(data[17]))
