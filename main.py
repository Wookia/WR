#!/usr/bin/python

import time
from ev3dev import *

lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
ts = touch_sensor(); assert ts.connected
cs = color_sensor(); assert cs.connected
ls = light_sensor(); assert ls.connected
lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

def scan(time, dir):
    global whiteLS
    global whiteCS
    global blackLS
    global blackCS
    global lmotor
    global rmotor
    global ls
    global cs
    i = 0
    while (i < time):
        lmotor.run_forever(speed_sp=dir*100)
        rmotor.run_forever(speed_sp=-dir*100)
        valLS = ls.value()
        valCS = cs.value()
        if (valLS > whiteLS):
            whiteLS = ls.value()
        elif (valLS < blackLS):
            blackLS = ls.value()

        if (valCS > whiteCS):
            whiteCS = cs.value()
        elif (valCS < blackCS):
            blackCS = cs.value()
        i+=1
    lmotor.stop()
    rmotor.stop()


while not ts.value():
    print("HWDP")
whiteLS = ls.value() 
whiteCS = cs.value()
blackLS = ls.value() 
blackCS = cs.value() 
scan(250, -1)
scan(250, 1)
scan(250, 1)
scan(250, -1)
print("WhiteLS: %s BlackLS: %s" %(whiteLS, blackLS))
print("WhiteCS: %s BlackCS: %s" %(whiteCS, blackCS))
while not ts.value():
	time.sleep(0.1)	
