"""
MASLAB sensor parsing module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""
import math

irVals = [0,0,0,0,0,0]
angArray = [-math.pi/2.0,-math.pi/4.0,0,math.pi/4.0,math.pi/2.0]

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

def test():
    print update([550,400,550,150,50],[5,5,0])
