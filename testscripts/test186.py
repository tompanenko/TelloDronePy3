
# Import the necessary modules
import socket
import threading
import time
from tello import Tello
import math

# Create Tello objects
h = Tello('192.168.1.186')

# Put Tellos into command mode
h.connect_wait()
time.sleep(2)
'''
# Takeoff
g.takeoff()
h.takeoff()
time.sleep(2)

gb = g.get_battery()
hb = h.get_battery()
print "g" + str(gb) + " " + "h" + str(hb)
time.sleep(1)
'''
for i in range(5):
	print h.get_battery()
	time.sleep(2)

'''
# Land
g.land()
h.land()
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)
'''
h.end()
