
# Import the necessary modules
import socket
import threading
import time
from tello2 import Tello

# Create Tello objects
h = Tello('192.168.1.186')
g = Tello('192.168.1.175')

# Put Tellos into command mode
g.connect_wait()
time.sleep(2)
h.connect_wait()
time.sleep(5)

# Takeoff
g.takeoff()
h.takeoff()
time.sleep(3)

# Read height and adust to match heights
while True:
	gh = g.get_distance_tof()
	hh = h.get_distance_tof()
	g.send_rc_control(0, 0, int(gh) - int(hh), 0)
        if h.get_height() > 250 or g.get_height() > 250:
		break
