"""
MASLAB sensor parsing module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""
import math

sensorParams = [
    (1750.0,26.625),
    (1750.0,26.625),
    (1750.0,26.625),
    (1750.0,26.625),
    (1750.0,26.625) ]

irVals = [0,0,0,0,0,0]
angArray = [math.pi/2.0,math.pi/4.0,0,-math.pi/4.0,-math.pi/2.0]

def rawToInches(valAndParams):
    #Converts a raw SHARP 2Y0A21 value to Inches. Good from 3" to 25"
    val,(m,a) = valAndParams
    return m/(val - a)

def serialLinkTransform(pose,angle,length):
    return [pose[0]+length*math.cos(pose[2]+angle),pose[1]+length*math.sin(pose[2]+angle)]
    
def update(rawVals, pose):
    #Takes in [five-tuple of raw IR sensor vals, ]
    global irVals
    output = []
    irVals = [rawToInches(x) for x in zip(rawVals,sensorParams)]
    for i in range(0,5):
        output.append([0,0,True])
        if (irVals[i] > 25.0 or irVals[i]<0):
            irVals[i] = 25.0
            output[i][2] = False
        [xVal,yVal] = serialLinkTransform(pose,angArray[i],irVals[i]+4.0)
        output[i][0] = xVal
        output[i][1] = yVal
    return output

def test():
    print update([550,400,550,150,50],[5,5,0])
