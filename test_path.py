#!/usr/bin/env python
from djitellopy import Tello
import time
import numpy as np

tello = Tello()

tello.connect()
tello.mission_pads_on()
try:
    tello.print_state()
    tello.takeoff()
    tello.print_state()
    for i in range(0, 4):
        tello.move_up(30)
        tello.print_state()
        tello.rotate_counter_clockwise(90)
        tello.print_state()
        tello.move_forward(30)
        tello.print_state()
        tello.move_down(30)
        tello.print_state()
    tello.land()
    tello.print_state()
finally:
    tello.end()
