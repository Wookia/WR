#!/usr/bin/python

from time import sleep
from ev3dev import *

lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
ts = touch_sensor(); assert ts.connected
cs = color_sensor(); assert cs.connected
ls = light_sensor(); assert ls.connected
lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'
whiteLS = None
whiteCS = None
blackLS = None
blackCS = None

def scan(time, dir):
    i = 0
    while (i < time):
        action_button(lmotor, dir*50)
        action_button(rmotor, -dir*50)
        valLS = ls.value()
        valCS = cs.value()
        if (valLS > whiteLS)
            whiteLS = ls.value()
        elif (valLS < blackLS)
            blackLS = ls.value()

        if (valCS > whiteCS)
            whiteCS = cs.value()
        elif (valCS < blackCS)
            blackCS = cs.value()
        i++


def action_button(motor, pwm):
    def roll(state):
        if state:
            motor.run_forever(duty_cycle_sp=pwm)
        else:
            motor.stop()
    return roll
while not ts.value():
    print("HWDP")
scan(1000, -1)
scan(1000, 1)
scan(1000, 1)
scan(1000, -1)
while not ts.value():
    print("WhiteLS: %s BlackLS: %s" %(whiteLS, blackLS))
    print("WhiteCS: %s BlackCS: %s" %(whiteCS, blackCS))
