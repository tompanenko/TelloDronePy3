#!/usr/bin/env python
''' Motion along a pre-programmed based on mission pads. Make sure pad 8 and 1 are visible to the drone after takeoff. '''
from djitellopy import Tello
import time

tello = Tello()

tello.connect()
tello.mission_pads_on()
try:
    tello.print_state()
    tello.takeoff()
    tello.print_state()
    tello.send_control_command('go 0 0 200 30 m8')
    time.sleep(5)
    tello.send_control_command('jump 0 0 100 180 m8 m1')
    tello.print_state()
    tello.land()
    tello.print_state()
finally:
    tello.end()
