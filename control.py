import os
import controller.control as ct
import vision.vision as v

def goForward():
    ct.setBasicControl(forward = 3.5)
def goBack():
    ct.setBasicControl(forward = -3.5)
def stop():
    ct.setBasicControl()
def turnLeft():
    ct.setBasicControl(angular=3.5)
def turnRight():
    ct.setBasicControl(angular=-3.5)
def disconnect():
    ct.stop()
    v.stop()

actions = {
    'f': goForward,
    'b': goBack,
    's': stop,
    'l': turnLeft,
    'r': turnRight,
    }
ct.initialize()
v.initialize('/dev/video1')
while True:
    a = raw_input()
    if a in actions:
        actions[a]()
    elif a == 'q':
        stop()
        disconnect()
        break
