# Import the necessary modules
import socket
import threading
import time
import math
from djitellopy import Tello

# Create Tello objects
tello1 = Tello('192.168.1.175')
tello2 = Tello('192.168.1.186')

# Length
l = 50

# Width
w = 50

# Speed
s = 50

# Put Tello into command mode
tello1.connect(False)
tello2.connect(False)
time.sleep(3)

# Takeoff 
tello1.takeoff(False)
tello2.takeoff(False)
time.sleep(4)

# Give space

tello1.move_forward(30, False)
time.sleep(3)
tello1.move_down(60, False)
tello2.move_down(80, False)
time.sleep(3)

# First cross
tello1.go_xyz_speed(0, -l, w, s)
tello2.go_xyz_speed(0, l, w, s)
time.sleep(math.sqrt(l*l + w*w) / s + 2)

# Second cross
tello1.go_xyz_speed(0, l, w, s)
tello2.go_xyz_speed(0, -l, w, s)
time.sleep(math.sqrt(l*l + w*w) / s + 2)

# Land
time.sleep(2)
tello1.land(False)
tello2.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

tello1.end()
tello2.end()
