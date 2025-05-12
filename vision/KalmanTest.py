import cv2
import numpy as np
import imutils
from math import sqrt
import time
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

# Initialize Kalman Filter
kalman = cv2.KalmanFilter(4, 2)  # 4 states (x, y, vx, vy), 2 measurements (x, y)

# State transition matrix (Assuming constant velocity model)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],  
                                    [0, 1, 0, 1],  
                                    [0, 0, 1, 0],  
                                    [0, 0, 0, 1]], np.float32)

# Measurement matrix (We can only measure x and y directly)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],  
                                     [0, 1, 0, 0]], np.float32)

# Process noise covariance (Adjust for smoother tracking)
kalman.processNoiseCov = np.array([[1, 0, 0, 0],  
                                   [0, 1, 0, 0],  
                                   [0, 0, 1, 0],  
                                   [0, 0, 0, 1]], np.float32) * 0.03  

# Measurement noise covariance (Adjust based on sensor noise)
kalman.measurementNoiseCov = np.array([[1, 0],  
                                       [0, 1]], np.float32) * 0.5  

# Initial state estimate
kalman.statePre = np.array([[0], [0], [0], [0]], np.float32)

# Initialize ball position
x2, y2 = 0, 0  # Predicted position
x, y = 0, 0  # Measured position from vision system
radius = 10

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #use these for green ball on table
    #lower_bound = np.array([65, 50, 85])
    #upper_bound = np.array([85, 110, 255])

    #green ball carr library
    lower_bound = np.array([48, 45, 203])
    upper_bound = np.array([68, 105, 263])
    frame = imutils.resize(frame, width=1200)
    #frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    #frame = frame[120:590, 160:1000]
    
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Threshold the HSV image to detect the orange ball
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Find contours in the mask
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)  
        if cv2.contourArea(c) > 50:  
            (x, y), _ = cv2.minEnclosingCircle(c)  

            # Prediction step (Predict the next position)
            predicted = kalman.predict()  # First predict the next state
            x2, y2 = predicted[0], predicted[1]  # Updated position after prediction

            # Generate a measurement with noise (optional)
            measurement = np.array([[np.float32(x)], [np.float32(y)]])
            # You can add random noise here if needed
            # randn(measurement, Scalar::all(0), Scalar::all(KF.measurementNoiseCov.at<float>(0)))

            # Measurement update (feeding in detected position)
            kalman.correct(measurement)  # Correct the prediction using the real measurement

    # Draw a circle around the predicted position
    cv2.circle(frame, (int(x2), int(y2)), int(radius), (255, 0, 0), 2)  # Blue for predicted

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
