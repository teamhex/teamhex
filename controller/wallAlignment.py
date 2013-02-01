"""
MASLAB Wall alignment module. 
DGonz@mit.edu
January 2013
"""

import PIDControlModule as pid
import math

alignTroller = pid.PIDController(1,.001,0.01)

done = True

def reset():
    global alignTroller,done
    alignTroller.setDesired(0,True)
    done = False
    return

def isDone():
    return done
    
def update(sensorVals):
    global alignTroller
    global done
    error = sensorVals[1]-sensorVals[3]
    if(abs(error)<.125 and not done):
        done = True
        return [0,0]
    elif(not done):
        return [0,alignTroller.update(error)]
    else:
        return [0,0]
