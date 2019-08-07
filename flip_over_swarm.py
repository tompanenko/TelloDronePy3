# Import the necessary modules
import socket
import threading
import time
import math
from djitellopy import Tello
from __builtin__ import False

# Create Tello objects
tello1 = Tello('192.168.1.175')
tello2 = Tello('192.168.1.186')

# Side length
l = 100

# Speed
s = 70

# Put Tello into command mode
tello1.connect(False)
tello2.connect(False)
time.sleep(7)

# Takeoff 
tello1.takeoff(False)
tello2.takeoff(False)
time.sleep(4)

tello1.move_left(150, False)
time.sleep(0.4)
tello2.flip_right()
time.sleep(4)
tello1.move_forward(40)
time.sleep(2.5)

tello1.move_right(150, False)
time.sleep(.6)
tello2.flip_left()
time.sleep(4)
tello1.move_forward(30)
time.sleep(2.5)

tello2.move_back(70)
time.sleep(3)
tello2.move_right(80)
time.sleep(4)
tello2.move_down(20)
time.sleep(3)

tello2.move_forward(120, False)
time.sleep(.2)
tello1.flip_back()
time.sleep(4)

tello2.move_back(120, False)
time.sleep(.5)
tello1.flip_forward()
time.sleep(4)


# Land
tello1.land(False)
tello2.land(False)
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

tello1.end()
tello2.end()

