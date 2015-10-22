#!/usr/bin/python

import time
from ev3dev import *

class States:

    readyToCalibrate = 1
    calibrating = 2
    readyToPrepare = 3
    preparing = 4
    readyToRun = 5
    running = 6
    #TODO: colision detector states?

class EV3:

    def __init__(self, States):
        self.lmotor = large_motor(OUTPUT_C); assert lmotor.connected
        self.rmotor = large_motor(OUTPUT_B); assert rmotor.connected
        self.ts = touch_sensor(); assert ts.connected
        self.cs = color_sensor(); assert cs.connected
        self.ls = light_sensor(); assert ls.connected
        self.lmotor.speed_regulation_enabled = 'on'
        self.rmotor.speed_regulation_enabled = 'on'
        self.States = States
        self.state = States.readyToCalibrate
    def changeLeftMotorSpeed(value):
        self.lmotor.run_forever(speed_sp=value)

    def changeRightMotorSpeed(value):
        self.rmotor.run_forever(speed_sp=value)

    def getLeftPickerValue():
        return self.cs.value()

    def getRightPickerValue():
        return self.ls.value()

    def stop():
        self.lmotor.stop()
        self.rmotor.stop()

#white>black
class Params:

    def __init__(self, EV3):
        self.EV3 = EV3
        self.whiteRight = EV3.getRightPickerValue()
        self.whiteLeft = EV3.getLeftPickerValue()
        self.blackRight = EV3.getRightPickerValue()
        self.blackLeft = EV3.getLeftPickerValue()

    def calibrate(time, error, calibrationSpeed):
        self.EV3.state = self.EV3.states.calibrating
        self.scan(time, -1)
        self.scan(time, 1)
        self.scan(time, 1)
        self.scan(time, -1)
        self.whiteRight = whiteRight - blackRight
        self.blackRight = 0
        self.whiteLeft = whiteLeft - blackLeft
        self.blackLeft = 0
        self.midRight = (whiteRight + blackRight)/2
        self.midLeft = (whiteLeft + blackLeft)/2
        #value from 0 to 1 (or 0% to 100%)
        self.error = error
        self.trueBlack = -1 + error
        self.trueWhite = 1 - error
        self.calibrationSpeed = calibrationSpeed
        self.EV3.state = self.EV3.states.readyToPrepare

    def scan(time, dir):
        i = 0
        while (i < time):
            self.EV3.changeLeftMotorSpeed(dir*self.calibrationSpeed)
            self.EV3.changeRightMotorSpeed(dir*self.calibrationSpeed)
            valLS = self.EV3.getRightPickerValue()
            valCS = self.EV3.getLeftPickerValue()
            if (valLS > self.whiteRight):
                self.whiteRight = valLS
            elif (valLS < self.blackRight):
                self.blackRight = valLS

            if (valCS > self.whiteLeft):
                self.whiteLeft = valCS
            elif (valCS < self.blackLeft):
                self.blackLeft = valCS
            i+=1
        self.EV3.stop()

class LineTracker:
    
    def __init__(self, Params):
        self.EV3 = Params.EV3
        self.Params = Params

    def leftColor():
        #value from 1+e to -1+e
        #positive value if more white
        #negative value if more black
        return (self.EV3.getLeftPickerValue() - self.Params.midLeft)/self.Params.midLeft

    def rightColor():
        #value from 1+e to -1+e
        #positive value if more white
        #negative value if more black
        return (self.EV3.getRightPickerValue() - self.Params.midRight)/self.Params.midRight

    def prepare():
        self.EV3.state = self.EV3.states.preparing
        i = 0
        crosedBlack = False
        while (i<1000):
            self.EV3.changeLeftMotorSpeed(-self.Params.calibrationSpeed)
            self.EV3.changeRightMotorSpeed(self.Params.calibrationSpeed)
            if(self.leftColor()<self.Params.trueBlack):
                crosedBlack = True
            if(crosedBlack):
                if(self.leftColor()>self.Params.trueWhite and self.rightColor()>self.Params.trueWhite):
                    self.EV3.stop()
                    self.EV3.state = self.EV3.states.readyToRun
                    break
            i += 1

    def run():
        self.counter()
        self.EV3.state = self.EV3.states.running
        #TODO: run line tracker

    def counter():
        sound.speak("3")
        time.sleep(0.7)
        sound.speak("2")
        time.sleep(0.7)
        sound.speak("1")
        time.sleep(0.7)
        sound.speak("ready")
        time.sleep(0.5)
        sound.speak("go")



EV3 = EV3()
Params = Params(EV3)
LineTracker = LineTracker(Params)
while not EV3.ts.value():
    print("Ready to calibrate + press button to run")
#calibrate(rotation "time", allowed error, calibration speed)
Params.calibrate(200, 0.1, 100)
while not EV3.ts.value():
    print("Ready to prepare + press button to run")
LineTracker.prepare()
while not EV3.ts.value():
    print("Ready to go + press button to run")
LineTrucker.run()
while not EV3.ts.value():
	time.sleep(0.1)
