"""
Super Serial
Rodrigo T. Gomes
rgomes@mit.edu
January 2013
"""

import os
import serial
import time

class Serial:
    def __init__(self, baudrate=115200, prestring='/dev/ttyACM'):
        self.baudrate = baudrate
        self.prestring = prestring
        self.connection = None

    def connect(self, port = None):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if port == None:
            for i in range(0,10):
                port = self.prestring+str(i)
                if os.path.exists(self.prestring+str(i)):
                    break
        self.connection = serial.Serial(port)
        self.connection.baudrate = self.baudrate
        self.connection.rtscts = True

    def send(self, msg):
        replied = False
        while not replied:
            #try:
            self.connection.timeout = None
            self.connection.write('S' + chr(len(msg)) + str(msg))
            self.connection.flushOutput()
            self.connection.timeout = 0.01
            if(self.connection.read() == 'E'):
                replied = True
            #except:
            #    print 'here'
            #    time.sleep(2)
            #    self.connect()
            #    self.send(msg)

    def receive(self):
        self.connection.timeout = None
        buf = ''
        size = 0
        while self.connection.read() != 'S':
            pass
        self.connection.timeout = 0.001
        buf = self.connection.read()
        if(buf != ''):
            size = ord(buf)
        buf = ''
        for i in xrange(size):
            buf = buf+self.connection.read()
        self.connection.write('E')
        return buf

    def stop(self):
        self.connection.close()

def test():
    s = Serial(baudrate = 1000000)
    print 'Connecting'
    s.connect(port = '/dev/ttyACM0')
    print 'connected'
    i = 0
    while(True):
        msg = 'aasdsadasdadsasakjsahdkjashdjkhasd'
        s.send(msg)
        print 'sent'
        if s.receive() != msg:
            i = i+1
            print i
            raw_input()
