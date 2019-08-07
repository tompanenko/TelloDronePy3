# Import the necessary modules
import socket
import Queue
import threading
import matplotlib.pyplot as plt
import time
import math
import stat
import numpy as np
from djitellopy import Tello


def track(tello2, time_q, pos_q, dt_q, final_q):
	x = 0
	y = 0
	z = 0
	init_time = time.time()
	prev_time = init_time
	while not stop:
		state_time =  tello2.wait_for_update()
		velx = float(tello2.get_vgx())
		vely = float(tello2.get_vgy())
		velz = float(tello2.get_vgz())
		time_q.put(time.time() - init_time)
		dt = state_time - prev_time
		dt_q.put(dt)
		prev_time = state_time
		print dt
		x = x + velx*dt
		y = y + vely*dt
		z = z + velz*dt
		#print x, y, z
		pos_q.put(x)
		print x, y, z
	final_q.put(x*(50/3.9))
	final_q.put(y*(-50/3.9))
	final_q.put(z*(-50/2.6))

def vel_track(tello1, tello2, q2, q1):
	while not stop:
		tello1.wait_for_update()
		velx2 = float(tello2.get_vgx())
		velx1 = float(tello1.get_vgx())
		q2.put(velx2)
		q1.put(velx1)
		

if __name__ == '__main__':

	# Create Tello object
	tello1 = Tello('192.168.1.175')
	tello2 = Tello('192.168.1.186')

	# Put Tello into command mode
	tello2.connect(False)
	tello1.connect(False)
	time.sleep(5)
	
	tello2.takeoff(False)
	tello1.takeoff(False)
	time.sleep(4)
	
	tello2.move_up(70, False)
	tello1.move_up(70, False)
	time.sleep(3)
	
	# Start velocity tracking thread
	q2 = Queue.Queue()
	q1 = Queue.Queue()
	global stop
	stop = False
	tracking_thread = threading.Thread(target=vel_track, args=(tello1, tello2, q2, q1,))
	tracking_thread.daemon = True
	tracking_thread.start()
	time.sleep(4)
	
	tello2.send_rc_control(0, 50, 0, 0)
	tello1.send_rc_control(0, 50, 0, 0)
	
	time.sleep(1)
	print 'waiting'
	while q2.get() == 0 and q1.get() == 0:
		velx2 = q2.get()
		velx1 = q1.get()
		print '1:', velx1, '\t2:', velx2
	
	time.sleep(1)
	
	print 'ready'
	start = time.time()
	while time.time() - start < 10:
		tello2.send_rc_control(0, 50, 0, 0)
		tello1.send_rc_control(0, 50, 0, 0)
		velx2 = q2.get()
		velx1 = q1.get()
		print '1:', velx1, '\t2:', velx2
		if velx2 < 0.2 or velx1 < 0.2:
			print 'block'
			
			tello2.move_back(30, False)
			tello1.move_back(30 ,False)
			time.sleep(2)
			
			tello2.send_rc_control(0, 50, 0, 0)
			tello1.send_rc_control(0, 50, 0, 0)
			time.sleep(3)
			
	
	tello1.stop(False)
	tello2.stop(False)
	time.sleep(2)
	
	tello1.land()
	tello2.land()
	
	tello1.end()
	tello2.end()