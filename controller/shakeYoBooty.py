"""
ShakeYoBooty
MASLAB 2013
dgonz@mit.edu
"""
import time

def shakeYoBooty(t):
    tStart = time.time()
    temp = time.time()
    while((time.time()-tStart)<t):
        if(time.time()-temp <.25):
            setForAngVels([0,3])
        elif(time.time()-temp <.5):
            temp = time.time()
            setForAngVels([0,-3])
    setForAngVels([0,0])
