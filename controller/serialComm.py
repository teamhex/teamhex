"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import superserial as serial
import struct

def initialize(contPort = '/dev/arduino_encoders', contBaud = 1000000):
    global serCont
    serCont = serial.Serial(baudrate=contBaud)
    serCont.connect(port=contPort)
    print "connected!"

def terminate():
    global serCont
    serCont.stop()
    
def sendCommand(command):
    global serCont
    serCont.send(command)

def receiveData():
    global serCont,serEnc
    while True:
        data = serCont.receive()
        if(len(data) == 8+5*2):
            return (struct.unpack('>l', data[0:4])[0],
                    struct.unpack('>l', data[4:8])[0],
                    ord(data[8])<<8 | ord(data[9]),
                    ord(data[10])<<8 | ord(data[11]),
                    ord(data[12])<<8 | ord(data[13]),
                    ord(data[14])<<8 | ord(data[15]),
                    ord(data[16])<<8 | ord(data[17]))
