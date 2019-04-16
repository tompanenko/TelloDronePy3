#!/usr/bin/env python
from djitellopy import Tello
import cv2
import numpy as np

img = np.zeros((200, 400))
cv2.putText(img, "Press any key here!", (40, 110), cv2.FONT_HERSHEY_SIMPLEX, 1,
            255)
cv2.imshow('State', img)
tello = Tello()
tello.connect()

try:
    while cv2.waitKey(50) == -1:
        tello.print_state()
finally:
    tello.end()
