#!/usr/bin/env python
from djitellopy import Tello
import cv2
import numpy as np
import image_face_processing as ifp

is_face_detection = True

img = np.zeros((500, 500))
cv2.imshow('pilot', img)

tello = Tello()

tello.connect()
tello.stream_on()
try:
    while cv2.waitKey(50) == -1:
        img = tello.get_frame()
        if img is not None:
            if is_face_detection:
                faces = ifp.image_faces(img)
                ifp.image_faces_rectangle(img, faces)
            cv2.imshow('pilot', img)
finally:
    tello.end()
