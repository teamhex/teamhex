import signal
import sys
import lib.superserial as ser
import struct
import math

irVals = [0,0,0,0,0,0]
angArray = [-math.pi/2.0,-math.pi/4.0,0,math.pi/4.0,math.pi/2.0]

def init():
	global serBoard
	serBoard = ser.Serial(1000000)
	serBoard.connect(port = "/dev/arduino_encoders")


def rawToInches(val):
    #Converts a raw SHARP 2Y0A21 value to Inches. Good from 3" to 25"
    return .3937*21.7/(val*5.0/1024.0-0.13)

def serialLinkTransform(pose,angle,length):
    return [pose[0]+length*math.cos(angle),pose[1]+length*math.sin(angle)]
    
def update(rawVals, pose):
    #Takes in [five-tuple of raw IR sensor vals, ]
    global irVals
    output = []
    irVals = [rawToInches(x) for x in rawVals]
    for i in range(0,5):
        output.append([0,0,True])
        if (irVals[i] > 25.0):
            irVals[i] = 25.0
            output[i][2] = False
        [xVal,yVal] = serialLinkTransform(pose,angArray[i],irVals[i]+4.0)
        output[i][0] = xVal
        output[i][1] = yVal
    return output


def receiveData():
	global serBoard
	while True:
		data = serBoard.receive()
		if(len(data) == 8+5*2):
			return (struct.unpack('>l',data[0:4])[0],
				struct.unpack('>l',data[4:8])[0],
				ord(data[8])<<8 | ord(data[9]),
				ord(data[10])<<8 | ord(data[11]),
				ord(data[12])<<8 | ord(data[13]),
				ord(data[14])<<8 | ord(data[15]),
				ord(data[16])<<8 | ord(data[17]))

def cleanQuit(signal, frame):
	print "Interrupt received"
	serBoard.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, cleanQuit)

init()
while True:
	print [rawToInches(x) for x in receiveData()[2:7]]
