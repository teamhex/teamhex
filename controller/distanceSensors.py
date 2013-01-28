"""
MASLAB sensor parsing module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""
import math

# To calibrate!
sensorParams = [
    (1677.11323903, -32.3694765169),
    (1677.11323903, -32.3694765169),
    (1677.11323903, -32.3694765169),
    (1677.11323903, -32.3694765169),
    (1677.11323903, -32.3694765169),]

# Maybe more?
maxDistance = [16.,16.,16.,16.,16.]
minDistance = [2.5,2.5,2.5,2.5,2.5]

irVals = [0,0,0,0,0,0]
angArray = [math.pi/2.0,math.pi/4.0,0,-math.pi/4.0,-math.pi/2.0]

def rawToInches(valAndParams):
    # Converts a raw SHARP 2Y0A21 value to Inches. Good from minDistance to maxDistance
    val,(m,a) = valAndParams
    if val-a != 0:
        return m/(val - a)
    else:
        return float("inf")

def serialLinkTransform(pose,angle,length):
    return [pose[0]+length*math.cos(pose[2]+angle),pose[1]+length*math.sin(pose[2]+angle)]
    
def update(rawVals, pose):
    # Takes in [five-tuple of raw IR sensor vals, pose]
    global irVals
    output = []
    irVals = [rawToInches(x) for x in zip(rawVals,sensorParams)]
    for i in xrange(5):
        output.append([0,0,True])
        if (not minDistance[i] < irVals[i] < maxDistance[i]):
            irVals[i] = maxDistance[i]
            output[i][2] = False
        [xVal,yVal] = serialLinkTransform(pose,angArray[i],irVals[i]+4.0)
        output[i][0] = xVal
        output[i][1] = yVal
    return output
