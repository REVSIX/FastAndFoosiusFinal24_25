import cv2
import numpy as np
import imutils
from math import sqrt
import time
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

# # Setup camera
# cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) #1920
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) #1080

# if not cap.isOpened():
#     print("Error: Could not open video capture device.")
#     exit()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame")
#         break
#     cv2.imshow('Frame', frame)  #show the circle on the frame in the camera feed

# cap.release()
# cv2.destroyAllWindows()



import cv2

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

# Open the video capture from the default camera (index 0)
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Change the index if you have multiple cameras
#camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Change the index if you have multiple cameras
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) #1920
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) #1080


if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Press 'q' to quit the video feed.")

while True:
    # Capture frame-by-frame
    ret, frame = camera.read()

    if not ret:
        print("Failed to grab frame.")
        break
    
    print(type(frame))
    frame = imutils.resize(frame, width=1200)  #resize frame
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
    frame = frame[120:590, 160:1000] #crops image to region of interest (table)
    # Display the resulting frame
    cv2.imshow("USB Camera Feed", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
camera.release()
cv2.destroyAllWindows()
