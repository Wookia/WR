#!/usr/bin/python

import time
from ev3dev import *

#Robot's states
class States:

    readyToCalibrate = 1
    calibrating = 2
    readyToPrepare = 3
    preparing = 4
    readyToRun = 5
    running = 6
    obstacleAvoiding = 7
    stop = 8

#this class represents all the robot's effectors and sensors
#2 "big" motors, one servo for the camera movement, touch sensor for starting, color/light sensors and the infrared
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
	#this methods changes the camera position
    def changeCameraMotorAngle(self, angle, speed):
        self.cameraMotor.run_to_rel_pos(position_sp=int(-angle*360),speed_sp=speed)

    def getLeftPickerValue(self):
        return self.ls.value()

    def getRightPickerValue(self):
        return self.cs.value()

    def getDistance(self):
        return self.ds.value()
	#this method does an empty while() loop while the left motor is still in motion
    def waitForRunningEnd(self):
        while ('running' in self.lmotor.state):
            i = 1
	#this method turns the robot through an angle
    def turnAngle(self, angle, speed):
        self.lmotor.run_to_rel_pos(position_sp=int(-angle*360),speed_sp=speed)
        self.rmotor.run_to_rel_pos(position_sp=int(angle*360),speed_sp=speed)
	#this method makes the robot run along a straight line (rotate the wheels through an angle)
    def runAngle(self, angle, speed):
        self.lmotor.run_to_rel_pos(position_sp=int(angle*360),speed_sp=speed)
        self.rmotor.run_to_rel_pos(position_sp=int(angle*360),speed_sp=speed)
	#this method checks whether the robot's left motor is in motion and returns a boolean accordingly
    def checkIfRunning(self):
        if 'running' in self.lmotor.state:
            return True
        return False
	#this method makes the 2 movement engines stop
    def stop(self):
        self.lmotor.stop()
        self.rmotor.stop()

#class representing the robot parameters and making him able to calibrate the sensors
class Params:

    def __init__(self, EV3):
        self.EV3 = EV3
        self.whiteRight = self.EV3.getRightPickerValue()
        self.whiteLeft = self.EV3.getLeftPickerValue()
        self.blackRight = self.EV3.getRightPickerValue()
        self.blackLeft = self.EV3.getLeftPickerValue()

	#the calibration method scanning the environment for "the blackest black" and "the whitest white" and scales it down to values from 0 to  n
	#this method uses the scan() method which does the necessary work connected with movement etc.
    def calibrate(self, time, calibrationSpeed):
        self.calibrationSpeed = calibrationSpeed
        self.maxDistance = 20
        self.scan(time, 1)
        self.scan(time, -1)
        self.scan(time, -1)
        self.trueBlackLeft = self.blackLeft
        self.trueBlackRight = self.blackRight
        self.whiteRight = self.whiteRight - self.blackRight
        self.blackRight = 0
        self.whiteLeft = self.whiteLeft - self.blackLeft
        self.blackLeft = 0
        self.midRight = (self.whiteRight + self.blackRight)/2
        self.midLeft = (self.whiteLeft + self.blackLeft)/2

    #the helper method for calibrate()
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
            i+=1
        self.EV3.stop()

#class with the functional program of a Line Follower w/obstacle avoiding method
class LineTracker:

    def __init__(self):
        self.States = States()
        self.EV3 = EV3(self.States)
        self.Params = Params(self.EV3)
        self.state = States.readyToCalibrate

	#this methods enables the robot to get only -1..1 values from color/light sensors (much better than hardcoding some values)
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
    #method aligning the robot to the line after calibration
    def prepare(self):
        self.state = self.States.preparing
        i = 0
        crosedBlack = False
        while (i<1000):
            self.EV3.changeLeftMotorSpeed(self.Params.calibrationSpeed)
            self.EV3.changeRightMotorSpeed(-self.Params.calibrationSpeed)
            if(self.leftColor()<-0.2):
                crosedBlack = True
            if(crosedBlack):
                if(self.leftColor()>=0.2 and self.rightColor()>=0.2):
                    self.EV3.stop()
                    self.EV3.state = self.States.readyToRun
                    break
            i += 1
    #the "preparation" method (button as a way of interacting with the user)
    def run(self):
        while True:
            if (self.state == self.States.readyToCalibrate):
                print("Ready to calibrate + press button to run")
                self.wait()
                self.state = self.States.calibrating
                self.Params.calibrate(200, 100)
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
                self.state = self.States.running
                self.trackLine()
            elif (self.state == self.States.stop):
                print("Stoped + press button to run")
                self.wait()
                self.state = self.States.running

    #line following method
    def trackLine(self):
        #left on white
        #right on white
        error = 0
        errorsSum = 0
        speed = 210
		#the Kp gain for the Proportional part, Ki for the Integrator
        Kp = 120
        Ki = 3.0
		#the "blackPower" variable is the gain applied to all the "black" readings
        blackPower = 4.5
        sumOfErrors = 0
        errorLimit = 300
		#the main program loop
        while(1 == 1):
            #obstacle test
            a = self.EV3.getDistance()
            if(a < self.Params.maxDistance):
                self.EV3.stop()
                self.avoidObstacle("left")
			#getting sensor readings
            right = self.rightColor()
            left = self.leftColor()
			#applying the gain if any readings are black
            right = right*blackPower if right < 0 else right
            left = left*blackPower if left < 0 else left
            error = (right - left)/2.0
            errorsSum = 0.99*errorsSum + error
            sumOfErrors = sumOfErrors + error
            #the crossroads case - both sensors on black line - do nothing (continue the PID control)
            if (left <-0.5*blackPower and right<-0.5*blackPower):
                leftSpeed = (int)(speed + error*Kp + Ki*errorsSum)
                rightSpeed = (int)(speed - error*Kp - Ki*errorsSum)
                self.EV3.changeLeftMotorSpeed(leftSpeed)
                self.EV3.changeRightMotorSpeed(rightSpeed)
            #the state automata part - turned on when the sum of errors is larger than some constant (in this case - 6)
            elif (left<-0.8*blackPower and abs(sumOfErrors) > 6):
                #we are turning left but too slow
                #stop right motor until we cross black line with right sensor
                self.EV3.changeRightMotorSpeed((int)(-0.7*speed))
                self.EV3.changeLeftMotorSpeed((int)(1.0*speed))
                while(1==1):
                    right = self.rightColor()
                    left = self.leftColor()
                    if(left>0 or right<0):
                        errosSum = 0
                        sumOfErrors = 0
                        break
                    time.sleep(0.005)
            #the state automata part - opposite direction
            elif (right<-0.8*blackPower and abs(sumOfErrors) > 6):
                #we are turning right but too slow
                #stop left motor until we cross black line with left sensor
                self.EV3.changeLeftMotorSpeed((int)(-0.7*speed))
                self.EV3.changeRightMotorSpeed((int)(1.0*speed))
                while(1==1):
                    left = self.leftColor()
                    right = self.rightColor()
                    if(right>0 or left<0):
                        errosSum = 0
                        sumOfErrors = 0
                        break
                    time.sleep(0.005)

            else:
                #PID control done when there are no "special cases"
                leftSpeed = (int)(speed + error*Kp + Ki*errorsSum)
                rightSpeed = (int)(speed - error*Kp - Ki*errorsSum)
                self.EV3.changeLeftMotorSpeed(leftSpeed)
                self.EV3.changeRightMotorSpeed(rightSpeed)
            time.sleep(0.005)


    #the obstacle avoiding method
    #it's basically a series of turns done by the distance sensor and the robot itself
    #direction:left/right
    def avoidObstacle(self, direction):
        speed = 200
        avoiding = True
        if(direction == 'left'):
            dir = -1
        else:
            dir = 1
        #turning  robot left/right and camera in opposite way and run until you dont see abstacle
        self.EV3.turnAngle(dir*0.43, speed)
        self.EV3.changeCameraMotorAngle(-dir*0.26, speed)
        self.EV3.waitForRunningEnd()
        self.EV3.runAngle(0.82, speed)
        self.EV3.waitForRunningEnd()
        while (self.EV3.getDistance() < self.Params.maxDistance + 6):
            self.EV3.changeLeftMotorSpeed(speed)
            self.EV3.changeRightMotorSpeed(speed)
        self.EV3.stop()
        #turning  robot left/right and run until you dont see abstacle
        self.EV3.turnAngle(-dir*0.42, speed)
        self.EV3.waitForRunningEnd()
        self.EV3.runAngle(0.7, speed)
        self.EV3.waitForRunningEnd()
        while (self.EV3.getDistance() < self.Params.maxDistance + 6):
            self.EV3.changeLeftMotorSpeed(speed)
            self.EV3.changeRightMotorSpeed(speed)
        self.EV3.stop()
        #turn camera to the start position and trun left/right
        self.EV3.changeCameraMotorAngle(dir*0.25, speed)
        self.EV3.runAngle(1, speed)
        self.EV3.waitForRunningEnd()
        self.EV3.turnAngle(-dir*0.34, speed)
        self.EV3.waitForRunningEnd()
        notPassedLeft = True
        notPassedRight = True
        #go until u didnt corss the road
        while (notPassedLeft or notPassedRight):
            self.EV3.changeLeftMotorSpeed(speed)
            self.EV3.changeRightMotorSpeed(speed)
            if (self.rightColor() < 0):
                notPassedRight = False
            if (self.leftColor() < 0):
                notPassedLeft = False
        while(1 == 1):
            if (self.rightColor() > 0 and self.leftColor() > 0):
                break
        crosedBlack = False
        #turn left/right untill you cross line with one sensors
        while(1 == 1):
            self.EV3.changeLeftMotorSpeed(-speed*dir)
            self.EV3.changeRightMotorSpeed(speed*dir)
            if(direction == "left"):
                if(self.leftColor()<0):
                    crosedBlack = True
                if(crosedBlack):
                    if(self.leftColor()>=0 and self.rightColor()>=0):
                        self.EV3.stop()
                        break
            else:
                if(self.rightColor()<0):
                    crosedBlack = True
                if(crosedBlack):
                    if(self.leftColor()>=0 and self.rightColor()>=0):
                        self.EV3.stop()
                        break
    #method allow to wait until button is pressed
    def wait(self):
        while not self.EV3.ts.value():
            time.sleep(0.01)


LineTracker = LineTracker()
LineTracker.run()
