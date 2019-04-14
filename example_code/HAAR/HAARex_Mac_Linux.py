import numpy as np
import cv2 as cv
from imutils.video import VideoStream
import time
import os
import argparse

'''
Parse Command Line Arguments

Arguments
---------
[0] Path to .xml file to use for Cascade.
    Default: ~/virtualenvs/facial_tracking/lib/python36/site-packages/cv2/data/haarcascade_frontalface_default.xml
[1] Index of Camera to use. Use default (0) to use built-in webcam. If another is plugged in, use (1)
    Default: 0
'''
parser = argparse.ArgumentParser(description='Code for Cascade Classifier tutorial.')

#Set path to trained frontal face .xml file for the Cascade Classifier to use
path = os.path.expanduser('~/virtualenvs/facial_tracking/lib/python36/site-packages/cv2/data/haarcascade_frontalface_default.xml')

parser.add_argument('--face_cascade', help='Path to face cascade.', default=path)
parser.add_argument('--camera', help='Camera devide number.', type=int, default=0)
args = parser.parse_args()

face_cascade_name = args.face_cascade

#Create a CascadeClassifier
face_cascade = cv.CascadeClassifier()

#-- 1. Load the cascades
if not face_cascade.load(face_cascade_name):
    print('--(!)Error loading face cascade')
    exit(0)

#Give user an update on progress
print('--LOADING CLASSIFIER FROM DISK')

#Setup a video feed from our webcam
vs = VideoStream().start()

#Give user an update on progress
print('--STARTING VIDEO STREAM')


#Let the camera sensor warm up for 3 seconds
time.sleep(3)

#Setup our running condition
running = True

while running:
    #Get a frame from the webcam
    frame = vs.read()

    #Convert the image to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    #Use the classifier to detect faces in the grayscale image
    #faces is a list of all faces found in the image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    #If there are more than 0 faces in the face list, draw a box around the face
    if len(faces) > 0:
        for (x,y,w,h) in faces:
            #Draw a BLUE box; openCV is BGR
            cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    #Show the output image in a window ("live feed")
    cv.imshow('frame',frame)

    #Quit the program if the user hits the "q" key on the keyboard
    if cv.waitKey(16) == ord('q'):
        break

#Stop Camera image acquisition
vs.stop()
