# Import the necessary modules
import socket
import threading
import time
import math
from djitellopy import Tello

# Create Tello objects
tello1 = Tello('192.168.1.175')
tello2 = Tello('192.168.1.186')
tello3 = Tello('192.168.1.178') 

# Side length
l = 100

# Speed
s = 70

# Put Tello into command mode
tello1.connect(False)
tello2.connect(False)
tello3.connect(False)
time.sleep(10)

# Takeoff 
tello1.takeoff(False)
tello2.takeoff(False)
tello3.takeoff(False)
time.sleep(4)

# Give space
tello2.move_up(int(math.sqrt(3)/2*l))
time.sleep(2)

# Triangle
tellos = [tello1, tello2, tello3]
for tello in tellos:
    tello.set_speed(s)
    time.sleep(0.5)
time.sleep(2)

for j in range(3):
    i = 3 - j
    print (i + 2) % 3 + 1
    tellos[(i + 2) % 3].move_right(l, False)
    print i % 3 + 1
    tellos[i % 3].go_xyz_speed(0, int(l/2), int(math.sqrt(3)/2 * l), s)
    print (i + 1) % 3 + 1
    tellos[(i + 1) % 3].go_xyz_speed(0, int(l/2), int(-1 * math.sqrt(3)/2 * l), s)
    time.sleep(4)
    
# Land
tello1.land(False)
tello2.land(False)
tello3.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

tello1.end()
tello2.end()
tello3.end()

