"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import lib.superserial as serial
import struct

def initialize(contPort = '/dev/arduino_encoders', contBaud = 1000000):
    global serCont
    serCont = serial.Serial(baudrate=contBaud)
    serCont.connect(port=contPort)
    print "connected!"
    
def sendCommand(command):
    global serCont
    serCont.send(command)

def receiveData():
    global serCont,serEnc
    while True:
        data = serCont.receive()
        if(len(data) == 8+5*2):
            return (ord(data[0])<<24 | ord(data[1]<<16 | ord(data[2])<<8 | ord(data[3]),
                    ord(data[4])<<24 | ord(data[5])<<16 | ord(data[6])<<8 | ord(data[7]),
                    ord(data[8])<<8 | ord(data[9]),
                    ord(data[10])<<8 | ord(data[11]),
                    ord(data[12])<<8 | ord(data[13]),
                    ord(data[14])<<8 | ord(data[15]),
                    ord(data[16])<<8 | ord(data[17]))
