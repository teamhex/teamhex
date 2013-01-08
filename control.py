import os
import serial
import time

class Serial:
    def __init__(self, baudrate=115200, prestring='/dev/ttyACM'):
        self.baudrate = baudrate
        self.prestring = prestring
        self.connection = None

    def connect(self, port = '/dev/ttyACM1'):
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
        try:
            print "Sending"
            self.connection.write('S' + str(msg) + 'E')
            self.connection.flushOutput()
            print 'S' + str(msg) + 'E'
        except:
            time.sleep(2)
            self.connect()
            self.send(msg)

    def stop(self):
        self.connection.close()

robot = Serial()
robot.connect()

ZERO = 127
def goForward():
    robot.send( chr(ZERO+70) + chr(ZERO+70))
def goBack():
    robot.send( chr(ZERO-70) + chr(ZERO-70))
def stop():
    robot.send( chr(ZERO) + chr(ZERO))
def turnLeft():
    robot.send( chr(ZERO+50) + chr(ZERO-50))
def turnRight():
    robot.send( chr(ZERO-50) + chr(ZERO+50))
def disconnect():
    robot.stop()

actions = {
    'f': goForward,
    'b': goBack,
    's': stop,
    'l': turnLeft,
    'r': turnRight,
    }
while True:
    a = raw_input()
    if a in actions:
        actions[a]()
    elif a == 'q':
        disconnect()
        break
