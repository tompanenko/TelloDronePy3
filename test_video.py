#!/usr/bin/env python
from djitellopy import Tello
import cv2
import numpy as np

tello = Tello()

tello.connect()
tello.streamon()
tello.keep_alive(continuous=True)

frame_reader = tello.get_frame_reader()

img = np.zeros((500, 500))
cv2.imshow('pilot', img)

while cv2.waitKey(50) == -1:
    print tello.state_str
    img = frame_reader.frame
    if img is not None:
        cv2.imshow('pilot', img)
cv2.destroyAllWindows()
cv2.waitKey(1)

tello.end()
