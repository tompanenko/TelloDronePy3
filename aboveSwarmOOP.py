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
d = 107

# Up down distance
l = 30

# Put Tello into command mode
g.connect(False)
h.connect(False)
time.sleep(3)

# Takeoff 
g.takeoff(False)
h.takeoff(False)
time.sleep(4)

# Go to different altitude
g.move_up(50, False)
time.sleep(3)

# Go above
g.move_right(d/2)
h.move_left(d/2 + 1)
time.sleep(5)

# Go up and down
for i in range(1):
  h.move_down(l, False)
  g.move_down(l, False)
  time.sleep(5)
 
  g.move_up(l, False)
  h.move_up(l, False)
  time.sleep(5)

# Separate
g.move_left(d/2 + 3)
h.move_right(d/2 + 3)
time.sleep(4)

# Land
time.sleep(2)
g.land(False)
h.land(False)
time.sleep(2)

# Print message
print("Mission completed successfully!")
time.sleep(1)

g.end()
h.end()
