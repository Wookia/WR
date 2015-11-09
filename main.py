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
    obstacleAvoiding = 7
    stop = 8
    #TODO: lastState

class EV3:

    def __init__(self, States):
        self.lmotor = large_motor(OUTPUT_C); assert self.lmotor.connected
        self.rmotor = large_motor(OUTPUT_B); assert self.rmotor.connected
        self.cameraMotor = medium_motor(OUTPUT_A); assert self.cameraMotor.connected
        self.ts = touch_sensor(); assert self.ts.connected
        self.cs = color_sensor(); assert self.cs.connected
        self.ls = light_sensor(); assert self.ls.connected
        self.ds = infrared_sensor(); assert self.ds.connected
        self.lmotor.speed_regulation_enabled = 'on'
        self.rmotor.speed_regulation_enabled = 'on'
        self.cameraMotor.speed_regulation_enabled = 'on'

    def changeLeftMotorSpeed(self, value):
        self.lmotor.run_forever(speed_sp=value)

    def changeRightMotorSpeed(self, value):
        self.rmotor.run_forever(speed_sp=value)

    def changeCameraMotorAngle(self, value):
        self.cameraMotor.run_forever(speed_sp=value)

    def getLeftPickerValue(self):
        return self.ls.value()

    def getRightPickerValue(self):
        return self.cs.value()

    def getDistance(self):
        return self.ds.value()

    def stop(self):
        self.lmotor.stop()
        self.rmotor.stop()

#white>black
class Params:

    def __init__(self, EV3):
        self.EV3 = EV3
        self.whiteRight = self.EV3.getRightPickerValue()
        self.whiteLeft = self.EV3.getLeftPickerValue()
        self.blackRight = self.EV3.getRightPickerValue()
        self.blackLeft = self.EV3.getLeftPickerValue()

    def calibrate(self, time, calibrationSpeed):
        self.calibrationSpeed = calibrationSpeed
        self.maxDistance = 0
        self.scan(time, -1)
        self.scan(time, 1)
        self.scan(time, 1)
        self.scan(time, -1)
        self.trueBlackLeft = self.blackLeft
        self.trueBlackRight = self.blackRight
        self.whiteRight = self.whiteRight - self.blackRight
        self.blackRight = 0
        self.whiteLeft = self.whiteLeft - self.blackLeft
        self.blackLeft = 0
        self.midRight = (self.whiteRight + self.blackRight)/2
        self.midLeft = (self.whiteLeft + self.blackLeft)/2
        #value from 0 to 1 (or 0% to 100%)
    def scan(self, time, dir):
        i = 0
        while (i < time):
            self.EV3.changeLeftMotorSpeed(dir*self.calibrationSpeed)
            self.EV3.changeRightMotorSpeed(-dir*self.calibrationSpeed)
            valLS = self.EV3.getRightPickerValue()
            valCS = self.EV3.getLeftPickerValue()
            valDS = self.EV3.getDistance()
            if (valLS > self.whiteRight):
                self.whiteRight = valLS
            elif (valLS < self.blackRight):
                self.blackRight = valLS

            if (valCS > self.whiteLeft):
                self.whiteLeft = valCS
            elif (valCS < self.blackLeft):
                self.blackLeft = valCS
            if (valDS>self.maxDistance):
                self.maxDistance = valDS
            i+=1
        self.EV3.stop()

class LineTracker:

    def __init__(self):
        self.States = States()
        self.EV3 = EV3(self.States)
        self.Params = Params(self.EV3)
        self.state = States.readyToCalibrate

    def leftColor(self):
        #value from 1+e to -1+e
        #positive value if more white
        #negative value if more black

        return ((self.EV3.getLeftPickerValue() - self.Params.trueBlackLeft) - self.Params.midLeft)/(1.0*self.Params.midLeft)

    def rightColor(self):
        #value from 1+e to -1+e
        #positive value if more white
        #negative value if more blac
        return ((self.EV3.getRightPickerValue() - self.Params.trueBlackRight) - self.Params.midRight)/(1.0*self.Params.midRight)

    def prepare(self):
        self.state = self.States.preparing
        i = 0
        crosedBlack = False
        while (i<1000):
            self.EV3.changeLeftMotorSpeed(self.Params.calibrationSpeed)
            self.EV3.changeRightMotorSpeed(-self.Params.calibrationSpeed)
            print("%s" % (int)(self.leftColor()*100))
            if(self.leftColor()<-0.6):
                crosedBlack = True
            if(crosedBlack):
                if(self.leftColor()>=0.6 and self.rightColor()<-0.6):
                    self.EV3.stop()
                    self.EV3.state = self.States.readyToRun
                    break
            i += 1

    def run(self):
        while True:
            if (self.state == self.States.readyToCalibrate):
                print("Ready to calibrate + press button to run")
                self.wait()
                self.state = self.States.calibrating
                self.Params.calibrate(400, 60)
                self.state = self.States.readyToPrepare
            elif (self.state == self.States.readyToPrepare):
                print("Ready to prepare + press button to run")
                self.wait()
                self.state = self.States.preparing
                self.prepare()
                self.state = self.States.readyToRun
            elif (self.state == self.States.readyToRun):
                print("Ready to go + press button to run")
                self.wait()
                #self.counter()
                self.state = self.States.running
                self.trackLine()
            elif (self.state == self.States.stop):
                print("Stoped + press button to run")
                self.wait()
                self.state = self.States.running

    def trackLine(self):
        #lewy na bialym
        #prawy na czarnym
        error = 0
        lastError = 0
        errorsSum = 0
        leftSpeed = 210
        rightSpeed = 210
        while(1 == 1):
            self.leftColor()
            if(self.leftColor() > 0 and self.rightColor() < 0):
                error = 0
            elif(self.leftColor() > 0 and self.rightColor() > 0):
                if(lastError == 0):
                    error = 1
                elif(lastError == -1):
                    error = -1
            elif(self.leftColor() < 0 || self.rightColor() > 0):
                error = -1
            errorsSum += error
            self.EV3.changeLeftMotorSpeed((int)(leftSpeed - error*90 - errorsSum * 0.2 - (error-lastError)*90))
            self.EV3.changeRightMotorSpeed((int)(rightSpeed + error*90 + errorsSum * 0.2 + (error-lastError)*90))
            lastError = error



    #dir:left/right
    def avoidObstacle(self, direction):
        leftSpeed = 210
        rightSpeed = 210
        avoiding = True
        modificator = 30
        if(direction == 'left'):
            dir = -1
        else:
            dir = 1
        timer = 1
        while (avoiding):
            if(self.EV3.getDistance>self.params.maxDistance):
                dir = dir * -1
                timer = -1 * timer
            if(timer=0):
                dir = 0

            self.EV3.changeLeftMotorSpeed(leftSpeed + dir*modificator)
            self.EV3.changeLeftMotorSpeed(leftSpeed - dir*modificator)
            timer = timer + 1


    def wait(self):
        while not self.EV3.ts.value():
            time.sleep(0.01)

    def counter(self):
        sound.speak("3")
        time.sleep(1)
        sound.speak("2")
        time.sleep(1)
        sound.speak("1")
        time.sleep(1)
        sound.speak("ready")
        time.sleep(1)
        sound.speak("go")
        time.sleep(1)


LineTracker = LineTracker()
LineTracker.run()
