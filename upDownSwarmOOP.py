# Import the necessary modules
import socket
import threading
import time
from djitellopy import Tello

# Create Tello objects
g = Tello('192.168.1.175')
h = Tello('192.168.1.186')

#Bounce distance
d = 100

# Put Tellos into command mode
g.connect(False)
h.connect(False)
time.sleep(3)

# Send the takeoff command
g.takeoff()
h.takeoff()
time.sleep(3)

#Go to top/bottom
g.move_down(d/2, False)
h.move_up(d/2, False)
time.sleep(3)

# Loop and move up and down
for i in range(1):
  g.move_up(d, False)
  h.move_down(d, False)
  time.sleep(4)
 
  g.move_down(d, False)
  h.move_up(d, False)
  time.sleep(4)

#Go to middle
g.move_up(d/2, False)
h.move_down(d/2, False)
time.sleep(3)

# Land
g.land(False)
h.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

g.end()
h.end()
