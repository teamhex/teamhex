"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import lib.superserial as serial
import struct

def initialize(contPort = '/dev/arduino_encoders', contBaud = 1000000, encPort = '/dev/arduino_control', encBaud = 115200):
    global serEnc,serCont
    serCont = serial.Serial(baudrate=contBaud)
    serCont.connect(port=contPort)
    serEnc = serial.Serial(baudrate=encBaud)
    serEnc.connect(port=encPort)
    print "connected!"
    
def sendCommand(command):
    global serCont
    serCont.send(command)

def receiveData():
    global serCont,serEnc
    while True:
        data = serCont.receive()
        data2 = serEnc.receive()
        if(len(data)+len(data2) == 8+5*2):
            return (struct.unpack('>l',data2[0:4])[0],
                    struct.unpack('>l',data2[4:8])[0],
                    ord(data[0])<<8 | ord(data[1]),
                    ord(data[2])<<8 | ord(data[3]),
                    ord(data[4])<<8 | ord(data[5]),
                    ord(data[6])<<8 | ord(data[7]),
                    ord(data[8])<<8 | ord(data[9]))
