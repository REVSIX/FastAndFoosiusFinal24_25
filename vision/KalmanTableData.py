'''
3/25/25:
The goal of this code is to test Kalman filtering configured for my laptop: ie. no
anti-fisheye cropping, etc needed. 
THis file writes a file saving an the data for time, x values, y values to be used in the Kalman Plot File

KalmanTableData is the version of this for the table

'''

import cv2
import numpy as np
import imutils
import time

from math import sqrt
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM


xVals = []
xpredictedVals = []
xcorrectedVals = []

yVals = []
ypredictedVals = []
ycorrectedVals = []

xvelcorrectedVals = []
yvelcorrectedVals = []


times = []


import json

def save_data():
    data = {
        "times": times,
        "xVals": xVals,
        "xpredictedVals": xpredictedVals,
        "xcorrectedVals": xcorrectedVals,
        "yVals": yVals,
        "ypredictedVals": ypredictedVals,
        "ycorrectedVals": ycorrectedVals,
        "xvelcorrectedVals": xvelcorrectedVals,
        "yvelcorrectedVals": yvelcorrectedVals
    }
    with open("kalman_data.json", "w") as f:
        json.dump(data, f)

def track_object():

    K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], 
                  [0.00000000e+00, 970.56156502, 385.82007021],
                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
    D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

    # Initialize Kalman Filter
    kalman = cv2.KalmanFilter(4, 2)  # 4 states (x, y, vx, vy), 2 measurements (x, y)

    # Initial transition matrix (will be updated with dt)
    kalman.transitionMatrix = np.array([[1, 0, 0, 0],  
                                        [0, 1, 0, 0],  
                                        [0, 0, 1, 0],  
                                        [0, 0, 0, 1]], np.float32)

    # Measurement matrix (We can only measure x and y directly)
    kalman.measurementMatrix = np.array([[1, 0, 0, 0],  
                                        [0, 1, 0, 0]], np.float32)

    # Process noise covariance (Adjust for smoother tracking)
    kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03   # initally .03, Q

    # Measurement noise covariance (Adjust based on sensor noise)
    kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5  #initially .5, R  

    # Initial state estimate
    kalman.statePre = np.array([[420], [235], [0], [0]], np.float32)
    kalman.statePost = kalman.statePre.copy()  # Sets initial corrected state

    # Initialize ball position
    x2, y2 = 420, 235  # Predicted position
    x, y = 420, 235  # Measured position from vision system
    radius = 10



    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Track the start time
    prev_time = time.time()
    start_time = time.time()

    # Main loop
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Resize and process the frame
        frame = imutils.resize(frame, width=1200)  #resize frame, so whole table is shown after resolution change above
        frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
        frame = frame[120:590, 160:1000] #crops image to region of interest (table)
        lower_bound = np.array([65, 50, 85])
        upper_bound = np.array([85, 110, 255])

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image to detect the ball
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        mask = cv2.medianBlur(mask, 5)  # Helps remove small noise
        # Find contours in the mask
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        


        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)  
            if cv2.contourArea(c) > 50:  
                (x, y), _ = cv2.minEnclosingCircle(c)  
                #print("Measurement:", x, y)
                # Calculate the time difference between frames
                current_time = time.time()
                elapsed_time = time.time()-start_time
                dt = current_time - prev_time  # Time difference in seconds
                prev_time = current_time  # Update previous time

                # Update the transition matrix with the new dt (time step)
                kalman.transitionMatrix = np.array([[1, 0, dt, 0],  
                                                    [0, 1, 0, dt],  
                                                    [0, 0, 1, 0],  
                                                    [0, 0, 0, 1]], np.float32)

                # Prediction step (Predict the next position)
                predicted = kalman.predict()  # First predict the next state
                x2, y2 = predicted[0].item(), predicted[1].item()  # Updated position after prediction

                # Measurement update (feeding in detected position)
                measurement = np.array([[np.float32(x)], [np.float32(y)]])
                corrected = kalman.correct(measurement)  # Correct the prediction using the real measurement
                x3, y3 = corrected[0].item(), corrected[1].item()  # Corrected position
                vx, vy = corrected[2].item(), corrected[3].item()

                xvelcorrectedVals.append(vx); yvelcorrectedVals.append(vy)

                xVals.append(x)
                xpredictedVals.append(x2)
                xcorrectedVals.append(x3)

                yVals.append(y)
                ypredictedVals.append(y2)
                ycorrectedVals.append(y3)

                times.append(elapsed_time)
                print(vx,vy)

                # Draw visualization circles
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)  # Red for measured
                cv2.circle(frame, (int(x2), int(y2)), int(radius), (255, 0, 0), 2)  # Blue for predicted
                cv2.circle(frame, (int(x3), int(y3)), int(radius), (0, 255, 0), 2)  # Green for corrected


        # Display the result
        cv2.imshow('Kalman Filter Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(xvelcorrectedVals)
            save_data()
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    track_object()



