import cv2
import numpy as np
import imutils
import time
import json
from AntiFisheye import AntiFisheye

# Lists to store collected data
xVals, xpredictedVals, xcorrectedVals = [], [], []
yVals, ypredictedVals, ycorrectedVals = [], [], []
times, vx_corrected, vy_corrected = [], [], []

# Function to save data for optimization
def save_data():
    data = {
        "times": times,
        "xVals": xVals,
        "xpredictedVals": xpredictedVals,
        "xcorrectedVals": xcorrectedVals,
        "yVals": yVals,
        "ypredictedVals": ypredictedVals,
        "ycorrectedVals": ycorrectedVals,
        "vx_corrected": vx_corrected,
        "vy_corrected": vy_corrected
    }
    with open("kalman_data.json", "w") as f:
        json.dump(data, f)

def track_object(Q=0.03, R=0.5):
    """ Tracks the ball and applies Kalman filtering with given Q and R values. """

    # Camera calibration matrix (example values)
    K = np.array([[968.82, 0, 628.93], 
                  [0, 970.56, 385.82], 
                  [0, 0, 1]])
    D = np.array([-0.045, -0.019, 0.082, -0.070])

    # Kalman Filter initialization
    kalman = cv2.KalmanFilter(4, 2)  # (4 states: x, y, vx, vy), (2 measurements: x, y)
    kalman.transitionMatrix = np.eye(4, dtype=np.float32)  # Identity matrix (will update dt)
    kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    kalman.processNoiseCov = np.eye(4, dtype=np.float32) * Q  
    kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * R  
    kalman.statePre = np.array([[0], [0], [0], [0]], np.float32)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    prev_time = time.time()
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = imutils.resize(frame, width=1200)
        frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
        frame = frame[120:590, 160:1000]

        lower_bound = np.array([65, 50, 85])
        upper_bound = np.array([85, 110, 255])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 50:
                (x, y), _ = cv2.minEnclosingCircle(c)

                current_time = time.time()
                elapsed_time = current_time - start_time
                dt = current_time - prev_time
                prev_time = current_time  

                kalman.transitionMatrix = np.array([[1, 0, dt, 0],  
                                                    [0, 1, 0, dt],  
                                                    [0, 0, 1, 0],  
                                                    [0, 0, 0, 1]], np.float32)

                predicted = kalman.predict()
                x2, y2 = predicted[0].item(), predicted[1].item()
                measurement = np.array([[np.float32(x)], [np.float32(y)]])
                corrected = kalman.correct(measurement)

                x3, y3 = corrected[0].item(), corrected[1].item()
                vx, vy = corrected[2].item(), corrected[3].item()

                xVals.append(x); xpredictedVals.append(x2); xcorrectedVals.append(x3)
                yVals.append(y); ypredictedVals.append(y2); ycorrectedVals.append(y3)
                vx_corrected.append(vx); vy_corrected.append(vy)
                times.append(elapsed_time)

                cv2.circle(frame, (int(x), int(y)), 10, (0, 0, 255), 2)  
                cv2.circle(frame, (int(x2), int(y2)), 10, (255, 0, 0), 2)  
                cv2.circle(frame, (int(x3), int(y3)), 10, (0, 255, 0), 2)  

        cv2.imshow('Kalman Filter Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            save_data()
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    track_object()
