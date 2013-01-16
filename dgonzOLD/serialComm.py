"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import lib.superserial as serial
import struct

port = '/dev/ttyACM0'
baud = 115200

def initialize(myPort = "/dev/ttyACM0", myBaud = 115200):
    global ser
    port = myPort
    baud = myBaud
    ser = serial.Serial(baudrate = myBaud)
    ser.connect(port=myPort)
    print "connected!"
    
def sendCommand(command):
    global ser
    ser.write(command)
    
def receive():
    global ser
    while True:
        data = ser.receive()
        if(len(data) == 8):
            return [struct.unpack('>l',data[0:4])[0],struct.unpack('>l',data[4:8])[0]]
