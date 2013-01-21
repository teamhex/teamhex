"""
MASLAB sensor parsing module
Daniel Gonzalez
dgonz@mit.edu
January 2013
"""
import math

sensorParams = [
    (852.413378416, -7.66621831311),
    (962.739023305, -19.3667541061),
    (1645.30186526, -6.22091620386),
    (897.604638959, 1.77016250212),
    (974.108058761, -12.0463125541)]

maxDistance = [10,10,20,10,10]

irVals = [0,0,0,0,0,0]
angArray = [math.pi/2.0,math.pi/4.0,0,-math.pi/4.0,-math.pi/2.0]

def rawToInches(valAndParams):
    #Converts a raw SHARP 2Y0A21 value to Inches. Good from 3" to maxDistance
    val,(m,a) = valAndParams
    if val-a != 0:
        return m/(val - a)
    else:
        return float("inf")

def serialLinkTransform(pose,angle,length):
    return [pose[0]+length*math.cos(pose[2]+angle),pose[1]+length*math.sin(pose[2]+angle)]
    
def update(rawVals, pose):
    #Takes in [five-tuple of raw IR sensor vals, ]
    global irVals
    output = []
    irVals = [rawToInches(x) for x in zip(rawVals,sensorParams)]
    for i in xrange(5):
        output.append([0,0,True])
        if (irVals[i] > maxDistance[i] or irVals[i]<0):
            irVals[i] = maxDistance[i]
            output[i][2] = False
        [xVal,yVal] = serialLinkTransform(pose,angArray[i],irVals[i]+4.0)
        output[i][0] = xVal
        output[i][1] = yVal
    return output

def test():
    print update([550,400,550,150,50],[5,5,0])
