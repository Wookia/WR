#!/usr/bin/python

import time
from ev3dev import *
class EV3:
    def __init__(self):
        self.lmotor = large_motor(OUTPUT_C); assert lmotor.connected
        self.rmotor = large_motor(OUTPUT_B); assert rmotor.connected
        self.ts = touch_sensor(); assert ts.connected
        self.cs = color_sensor(); assert cs.connected
        self.ls = light_sensor(); assert ls.connected
        self.lmotor.speed_regulation_enabled = 'on'
        self.rmotor.speed_regulation_enabled = 'on'

class Params:
    def __init__(self):
        self.whiteLS = ev3.ls.value()
        self.whiteCS = ev3.cs.value()
        self.blackLS = ev3.ls.value()
        self.blackCS = ev3.cs.value()
    def calibrate(EV3, time):
        self.scan(EV3, time, -1)
        self.scan(EV3, time, 1)
        self.scan(EV3, time, 1)
        self.scan(EV3, time, -1)
    def scan(EV3, time, dir):
        i = 0
        while (i < time):
            EV3.lmotor.run_forever(speed_sp=dir*100)
            EV3.rmotor.run_forever(speed_sp=-dir*100)
            valLS = EV3.ls.value()
            valCS = EV3.cs.value()
            if (valLS > whiteLS):
                whiteLS = valLS
            elif (valLS < blackLS):
                blackLS = valLS

            if (valCS > whiteCS):
                whiteCS = valCS
            elif (valCS < blackCS):
                blackCS = valCS
            i+=1
        lmotor.stop()
        rmotor.stop()


EV3 = ev3()
Params = Params()
while not EV3.ts.value():
    print("HWDP")
Params.calibrate(EV3, 250)
print("WhiteLS: %s BlackLS: %s" %(Params.whiteLS, Params.blackLS))
print("WhiteCS: %s BlackCS: %s" %(Params.whiteCS, Params.blackCS))
while not EV3.ts.value():
	time.sleep(0.1)
