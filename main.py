#!/usr/bin/python

from time import sleep
from ev3dev import *

lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
irsens = infrared_sensor();     assert irsens.connected

rc = remote_control(irsens)

lmotor.set(speed_regulation_enabled='off', stop_command='brake')
rmotor.set(speed_regulation_enabled='off', stop_command='brake')

def action_button(motor, pwm):
    def roll(state):
        if state:
            motor.run_forever(duty_cycle_sp=pwm)
        else:
            motor.stop()
    return roll

rc.on_red_up   (action_button(lmotor,  100))
rc.on_red_down (action_button(lmotor, -100))
rc.on_blue_up  (action_button(rmotor,  100))
rc.on_blue_down(action_button(rmotor, -100))

while True:
    rc.process()
    sleep(0.01)
