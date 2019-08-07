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
d = 107

# Up down distance
l = 30

# Put Tello into command mode
tello1.connect(False)
tello2.connect(False)
time.sleep(3)

# Takeoff 
tello1.takeoff(False)
tello2.takeoff(False)
time.sleep(4)

# Go to different altitude
tello1.move_up(50, False)
time.sleep(3)

# Go above
tello1.move_right(d/2)
tello2.move_left(d/2 + 1)
time.sleep(5)

# Go up and down
for i in range(1):
    tello2.move_down(l, False)
    tello1.move_down(l, False)
    time.sleep(5)
    tello1.move_up(l, False)
    tello2.move_up(l, False)
    time.sleep(5)

# Separate
tello1.move_left(d/2 + 3)
tello2.move_right(d/2 + 3)
time.sleep(4)

# Land
time.sleep(2)
tello1.land(False)
tello2.land(False)
time.sleep(2)

# Print message
print("Mission completed successfully!")
time.sleep(1)

tello1.end()
tello2.end()
