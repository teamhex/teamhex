"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import serial
import struct

port = '/dev/ttyACM0'
baud = 115200
ser = serial.Serial()

def initialize(myPort = "/dev/ttyACM0", myBaud = 115200):
    global ser
    port = myPort
    baud = myBaud
    ser = serial.Serial(myPort,myBaud)
    
def sendCommand(command):
    global ser
    ser.write(command)
    
def receive():
    global ser
    data = ser.readline()
    if(data[0]=='S' and data[len(data)-3]=='E'):
        data = data[1:len(data)-3]
        data= [struct.unpack('>l',data[0:4])[0],struct.unpack('>l',data[4:8])[0]]
        return data
    else:
        return receive()
