# Import the necessary modules
import socket
import threading
import time
from djitellopy import Tello

# Create Tello objects
tello1 = Tello('192.168.1.175')
tello2 = Tello('192.168.1.186')

#Bounce distance
d = 100

# Put Tellos into command mode
tello1.connect(False)
tello2.connect(False)
time.sleep(3)

# Send the takeoff command
tello1.takeoff()
tello2.takeoff()
time.sleep(3)

#Go to top/bottom
tello1.move_down(d/2, False)
tello2.move_up(d/2, False)
time.sleep(3)

# Loop and move up and down
for i in range(1):
    tello1.move_up(d, False)
    tello2.move_down(d, False)
    time.sleep(4)
    tello1.move_down(d, False)
    tello2.move_up(d, False)
    time.sleep(4)

#Go to middle
tello1.move_up(d/2, False)
tello2.move_down(d/2, False)
time.sleep(3)

# Land
tello1.land(False)
tello2.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

tello1.end()
tello2.end()
