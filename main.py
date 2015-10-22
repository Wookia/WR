#!/usr/bin/python

import time
from ev3dev import *
class EV3:
    def __init__(self):
        self.lmotor = large_motor(OUTPUT_C); assert self.lmotor.connected
        self.rmotor = large_motor(OUTPUT_B); assert self.rmotor.connected
        self.ts = touch_sensor(); assert self.ts.connected
        self.cs = color_sensor(); assert self.cs.connected
        self.ls = light_sensor(); assert self.ls.connected
        self.lmotor.speed_regulation_enabled = 'on'
        self.rmotor.speed_regulation_enabled = 'on'

class Params:
    def __init__(self, EV3):
        self.whiteLS = EV3.ls.value()
        self.whiteCS = EV3.cs.value()
        self.blackLS = EV3.ls.value()
        self.blackCS = EV3.cs.value()
    def calibrate(self, EV3, time):
        self.scan(EV3, time, -1)
        self.scan(EV3, time, 1)
        self.scan(EV3, time, 1)
        self.scan(EV3, time, -1)
    def scan(self, EV3, time, dir):
        i = 0
        while (i < time):
            EV3.lmotor.run_forever(speed_sp=dir*100)
            EV3.rmotor.run_forever(speed_sp=-dir*100)
            valLS = EV3.ls.value()
            valCS = EV3.cs.value()
            if (valLS > self.whiteLS):
                self.whiteLS = valLS
            elif (valLS < self.blackLS):
                self.blackLS = valLS

            if (valCS > self.whiteCS):
                self.whiteCS = valCS
            elif (valCS < self.blackCS):
                self.blackCS = valCS
            i+=1
        EV3.lmotor.stop()
        EV3.rmotor.stop()


EV3 = EV3()
Params = Params(EV3)
while not EV3.ts.value():
    print("HWDP")
Params.calibrate(EV3, 250)
print("WhiteLS: %s BlackLS: %s" %(Params.whiteLS, Params.blackLS))
print("WhiteCS: %s BlackCS: %s" %(Params.whiteCS, Params.blackCS))
while not EV3.ts.value():
	time.sleep(0.1)
