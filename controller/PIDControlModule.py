"""
PID Control module
Daniel J. Gonzalez
dgonz@mit.edu
November 2012
"""

class PIDController():
    def __init__(self,mykP = 1, mykI = 0, mykD = 0):
        self.kP = mykP
        self.kI = mykI
        self.kD = mykD
        self.xDesired = 0
        self.xError = 0
        self.dXError = 0
        self.xErrorPrevious = 0
        self.xErrorIntegral = 0
        #print "PID Controller Initialized"
    def setKP(self,mykP):
        self.kP = mykP
    def setKI(self,mykI):
        self.kI = mykI
    def setKD(self,mykD):
        self.kD = mykD
    def setDesired (self,myxDesired,reset = False):
        self.xDesired = myxDesired
        if (reset):
            self.xErrorIntegral = 0
            self.xError = 0
            self.dXError = 0
            self.xErrorPrevious = 0
            self.xErrorIntegral = 0
    def getDesired(self):
        return self.xDesired
    def update(self,xSense):
        self.xError = self.xDesired - xSense
        self.dXError = self.xError - self.xErrorPrevious
        self.command = self.kP * self.xError + self.kI * self.xErrorIntegral + self.kD * self.dXError
        self.xErrorPrevious = self.xError
        self.xErrorIntegral+= self.xError
        return self.command
