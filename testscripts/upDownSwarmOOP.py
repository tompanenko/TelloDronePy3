# Import the necessary modules
import socket
import threading
import time
from tello import Tello

# Create Tello objects
grace = Tello('192.168.1.175')
harmony = Tello('192.168.1.186')

#Bounce distance
d = 100

# Put Tellos into command mode
grace.connect()
harmony.connect()
time.sleep(1)

# Send the takeoff command
grace.takeoff()
harmony.takeoff()
time.sleep(3)

#Go to top/bottom
grace.move('down', d/2)
harmony.move('up', d/2)
time.sleep(3)

# Loop and move up and down
for i in range(1):
  grace.move('up', d)
  harmony.move('down', d)
  time.sleep(3)
 
  grace.move('down', d)
  harmony.move('up', d)
  time.sleep(3)

#Go to middle
grace.move('up', d/2)
harmony.move('down', d/2)
time.sleep(3)

# Land
grace.land()
harmony.land()
time.sleep(3)

# Print message
print("Mission completed successfully!")
time.sleep(1)

grace.end()
harmony.end()
