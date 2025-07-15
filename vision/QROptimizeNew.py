import numpy as np
import json
import scipy.optimize as opt

import cv2
import numpy as np
import imutils
import time
import json
from AntiFisheye import AntiFisheye



def track_object(Q, R):

    # Lists to store collected data
    xVals, xpredictedVals, xcorrectedVals = [], [], []
    yVals, ypredictedVals, ycorrectedVals = [], [], []
    times, vx_corrected, vy_corrected = [], [], []

    Q = np.float32(Q)
    R = np.float32(R)
    """ Tracks the ball and applies Kalman filtering with given Q and R values. """

    # Camera calibration matrix (example values)
    K = np.array([[968.82, 0, 628.93], 
                  [0, 970.56, 385.82], 
                  [0, 0, 1]])
    D = np.array([-0.045, -0.019, 0.082, -0.070])

    # Kalman Filter initialization
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
    kalman.processNoiseCov = np.eye(4, dtype=np.float32) * Q   

    # Measurement noise covariance (Adjust based on sensor noise)
    kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * R  

    # Initial state estimate
    kalman.statePre = np.array([[0], [0], [0], [0]], np.float32)

    # Initialize ball position
    x2, y2 = 0, 0  # Predicted position
    x, y = 0, 0  # Measured position from vision system
    radius = 10

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    prev_time = time.time()
    start_time = time.time()

    for _ in range(200):
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
        mask = cv2.medianBlur(mask, 5)  # Helps remove small noise

        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        if len(contours) > 0:
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
                #print(vx,vy)
                

                cv2.circle(frame, (int(x), int(y)), radius, (0, 0, 255), 2)  
                cv2.circle(frame, (int(x2), int(y2)), radius, (255, 0, 0), 2)  
                cv2.circle(frame, (int(x3), int(y3)), radius, (0, 255, 0), 2)
        
        #print(x,y)
        cv2.imshow('Kalman Filter Tracking', frame)

    cap.release()
    print()
    cv2.destroyAllWindows()




    return xVals,xpredictedVals,xcorrectedVals,yVals,ypredictedVals,ycorrectedVals,times,vx_corrected,vy_corrected


def cost_function(params):
    Q, R = params
    print("Q, R:",Q,R)
    print()
    xVals,xpredictedVals,xcorrectedVals,yVals,ypredictedVals,ycorrectedVals,times,vx_corrected,vy_corrected = track_object(Q,R)
    

    # crop out inital instability from what's being past into cost function

    split = 100
    xVals = xVals[split:]
    xpredictedVals = xpredictedVals[split:]
    xcorrectedVals = xcorrectedVals[split:]

    yVals = yVals[split:]
    ypredictedVals = ypredictedVals[split:]
    ycorrectedVals = ycorrectedVals[split:]

    times = times[split:]

    vx_corrected = vx_corrected[split:]
    vy_corrected = vy_corrected[split:]
    print("vxcorrected", vx_corrected)

    vx_corrected = np.array(vx_corrected, dtype=np.float32)
    vy_corrected = np.array(vy_corrected, dtype=np.float32)
    x_corrected = np.array(xcorrectedVals, dtype=np.float32)
    y_corrected = np.array(ycorrectedVals, dtype=np.float32)
    x_measured = np.array(xVals, dtype=np.float32)
    y_measured = np.array(yVals, dtype=np.float32)

    #print("vxcorrected:", vx_corrected)

    speed = np.sqrt(vx_corrected**2 + vy_corrected**2)
    moving_mask = speed > 1.0  
    stationary_mask = ~moving_mask
    #print("speed", speed )
    #print("moving mask:", moving_mask)
    #print()

    if np.any(stationary_mask):
        fluctuation_penalty = np.var(x_corrected[stationary_mask]) + np.var(y_corrected[stationary_mask])
    else:
        fluctuation_penalty = 0
    
    if np.any(moving_mask):
        lag_penalty = np.mean(np.abs(x_corrected[moving_mask] - x_measured[moving_mask])) + \
                    np.mean(np.abs(y_corrected[moving_mask] - y_measured[moving_mask]))
    else:
        lag_penalty = 0

    print("fluc", fluctuation_penalty)
    print("lag", lag_penalty)

    print("cost", 2 * fluctuation_penalty + 10 * lag_penalty)


    print()
    return 2 * fluctuation_penalty + 10 * lag_penalty


bounds = [(.01, .7), (.01, .7)]
time.sleep(5)
#initial_params = [.03, .5]
# initial_params = np.array([
#     [0.01, 0.2],
#     [0.1, 0.2],
#     [0.1, 0.2],
#     [0.1, 0.2],
#     [0.1, 0.2]
# ])


xVals,xpredictedVals,xcorrectedVals,yVals,ypredictedVals,ycorrectedVals,times,vx_corrected,vy_corrected = track_object(Q,R)

result = opt.differential_evolution(cost_function, bounds, strategy='best1bin', maxiter=10,  tol=0.1, popsize=15, disp=True)

optimal_Q, optimal_R = result.x
print(f"Optimal Q: {optimal_Q}, Optimal R: {optimal_R}")

