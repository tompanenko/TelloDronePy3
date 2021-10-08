#!/usr/bin/env python
import socket
import threading
import time
from djitellopy import Tello

# Create Tello objects
tello = Tello('192.168.1.175')

# Distance
d = 30

# Put Tellos into command mode
tello.connect()
time.sleep(3)

# Send the takeoff command
tello.takeoff()
time.sleep(3)

# # Test move commands
# tello.move_forward(d)
# time.sleep(1)
# tello.move_back(d)
# time.sleep(1)
# tello.move_left(d)
# time.sleep(1)
# tello.move_right(d)
# time.sleep(1)
# tello.move_up(d)
# time.sleep(1)
# tello.move_down(d)
# time.sleep(1)

# # Test rotate commands
# tello.rotate_cw(d)
# time.sleep(1)
# tello.rotate_ccw(d)
# time.sleep(1)

# # Test flips
# tello.flip_forward()
# time.sleep(1)
# tello.flip_back()
# time.sleep(1)
# tello.flip_left()
# time.sleep(1)
# tello.flip_right()
# time.sleep(1)

# Land
tello.land()
time.sleep(3)

# Print message
print("Mission completed")
time.sleep(1)

tello.end()
