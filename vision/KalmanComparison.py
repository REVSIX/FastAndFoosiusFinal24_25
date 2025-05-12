import cv2
import numpy as np
import imutils
import time

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
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03   # initally .03

# Measurement noise covariance (Adjust based on sensor noise)
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5  #initially .5  

# Initial state estimate
kalman.statePre = np.array([[0], [0], [0], [0]], np.float32)

# Initialize ball position
x2, y2 = 0, 0  # Predicted position
x, y = 0, 0  # Measured position from vision system
radius = 10

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Track the start time
prev_time = time.time()

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Resize and process the frame
    frame = imutils.resize(frame, width=1200)
    lower_bound = np.array([65, 50, 85])
    upper_bound = np.array([85, 110, 255])

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to detect the ball
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Find contours in the mask
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)  
        if cv2.contourArea(c) > 50:  
            (x, y), _ = cv2.minEnclosingCircle(c)  

            # Calculate the time difference between frames
            current_time = time.time()
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

            # Draw visualization circles
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)  # Red for measured
            cv2.circle(frame, (int(x2), int(y2)), int(radius), (255, 0, 0), 2)  # Blue for predicted
            cv2.circle(frame, (int(x3), int(y3)), int(radius), (0, 255, 0), 2)  # Green for corrected

    # Display the result
    cv2.imshow('Kalman Filter Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
