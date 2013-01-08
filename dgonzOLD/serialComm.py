"""
MASLAB Serial Communication Module
Daniel J. Gonzalez
dgonz@mit.edu
January 2013
"""

import serial

port = '/dev/ttyACM0'
baud = 400000
ser = serial.Serial()

def initialize(myPort = "/dev/ttyACM0", myBaud = 400000):
    global ser
    port = myPort
    baud = myBaud
    ser = serial.Serial(myPort,myBaud)
    
    
def sendCommand(command):
    global ser
    ser.write(command)
    
def receive():
    global ser
    ser.write('E')
    data = ser.readline()
    if(data[0]=='S' and data[len(data)-3]=='E'):
        data = data[1:len(data)-3].split(',')
        data = [int(x) for x in data]
        return data
    else:
        return receive()
