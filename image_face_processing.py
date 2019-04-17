#!/usr/bin/env python
"""
Utilities for handling face detection
"""
import cv2
import os.path

#Path for xml file with cascade data (autoselect among candidate locations)
PATH_CASCADE_XML_LIST = [
    'haarcascade_frontalface_default.xml'
    '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
    '/Users/tron/Documents/miniconda2/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml'
]

for PATH_CASCADE_XML in PATH_CASCADE_XML_LIST:
    if os.path.isfile(PATH_CASCADE_XML):
        break

#Load cascade into global object
FACE_CASCADE = cv2.CascadeClassifier(PATH_CASCADE_XML)


def image_faces(img):
    """ Runs face detection on the image, and returns list of bounding boxes """
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
    return faces


def image_faces_rectangle(img, faces):
    """ Adds a green rectangle around each detected face """
    for (x, y, w, h) in faces:
        image_rectangle(img, x, y, w, h)
    return img


def image_rectangle(img, x, y, w, h):
    """ Adds a green rectangle to the image """
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))
    return img
