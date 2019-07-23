# Import the necessary modules
import socket
import threading
import time
import math
from djitellopy import Tello

# Create Tello objects
g = Tello('192.168.1.175')
h = Tello('192.168.1.186')

# Length
l = 50

# Width
w = 50

# Speed
s = 50

# Put Tello into command mode
g.connect(False)
h.connect(False)
time.sleep(3)

# Takeoff 
g.takeoff(False)
h.takeoff(False)
time.sleep(4)

# Give space

g.move_forward(30, False)
time.sleep(3)
g.move_down(60, False)
h.move_down(80, False)
time.sleep(3)

# First cross
g.go_xyz_speed(0, -l, w, s)
h.go_xyz_speed(0, l, w, s)
time.sleep(math.sqrt(l*l + w*w) / s + 2)

# Second cross
g.go_xyz_speed(0, l, w, s)
h.go_xyz_speed(0, -l, w, s)
time.sleep(math.sqrt(l*l + w*w) / s + 2)

# Land
time.sleep(2)
g.land(False)
h.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

g.end()
h.end()
