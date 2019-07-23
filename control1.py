# Import the necessary modules
import socket
import threading
import re
import time
import math
from djitellopy import Tello

# Create Tello objects
h = Tello('192.168.1.175')
#g = Tello('192.168.1.175')

# Put Tello into command mode
h.connect()
time.sleep(2)
udMid = 730
land = True
emergency = False

lrVel = 0
fbVel = 0
udVel = 0
turnVel = 0

# Wait for control drone to be picked up so flight can begin
while land:
	try:
		tof = float(re.sub("[^0-9]", "", h.get_distance_tof()))
		print tof
		if tof > 100:
			#g.takeoff()
			print 'takeoff'
			land = False
	except ValueError:
		print 'TOF not a float'

# Read state of control drone and send commands to flying drone 
while not land and not emergency:
	try:
		tof = float(re.sub("[^0-9]", "", h.get_distance_tof()))
		tofDiff = tof - udMid
		udVel = 0
		if abs(tofDiff) > 30:
			udVel = tofDiff / 5
			if tof == 100:
				land = True
			elif tofDiff > 400:
				udVel = 80
			elif tofDiff < -400:
				udVel = -80
	except ValueError:
		print 'TOF not a float'
		udVel = 0

	att = str.split(h.get_attitude(), ';')
	print att

	try:
		pitch = float(re.sub("[^0123456789-]", "", att[0])) # + = back
		fbVel = 0
		if abs(pitch) > 10:
			fbVel = pitch * -1.5
			if pitch > 50:
				fbVel = -80
			elif pitch < -50:
				fbVel = 80
	except ValueError:
		print 'pitch not a float'
		fbVel = 0
		
	try:		
		roll = float(re.sub("[^0123456789-]", "", att[1])) # + = right
		lrVel = 0
		if abs(roll) > 10:
			lrVel = roll * 1.5
			if abs(roll) > 160:
				emergency = True
			elif roll > 50:
				lrVel = 80
			elif roll < -50:
				lrVel = -80
	except ValueError:
		print 'roll not a float'
		lrVel = 0

	try:		
		yaw = float(re.sub("[^0123456789-]", "", att[2])) # + = cw(right)
		turnVel = 0
		if abs(yaw) > 10:
			turnVel = yaw * 1.5
			if yaw > 50:
				turnVel = 80
			elif yaw < -50:
				turnVel = -80
	except ValueError:
		print 'yaw not a float'
		turnVel = 0


	#g.send_rc_control(lrVel, fbVel, udVel, turnVel)
	print roll, '\t', pitch, '\t', tofDiff, '\t', yaw 
	print lrVel,'\t', fbVel, '\t', udVel, '\t', turnVel

	'''
	if(lrVel > 0):
		a = 'right'
	elif(lrVel < 0):
		a = 'left'
	else:
		a = 'stay'

	if(fbVel > 0):
		b = 'forward'
	elif(fbVel < 0):
		b = 'back'
	else:
		b = 'stay'
	
	if(udVel > 0):
		c = 'up'
	elif(udVel < 0):
		c = 'down'
	else:
		c = 'stay'

	if(turnVel > 0):
		d = 'right'
	elif(turnVel < 0):
		d = 'left'
	else:
		d = 'stay'

	print a, b, c, d
	'''

	if land:
		print 'land'
		#g.land()
	if emergency:
		print 'emergency'
		#g.emergency()
		break

#g.end()
h.end()
