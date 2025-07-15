'''
This is the second version of mainKalmanPlot.py with the goal of ensured that times and
pastTimes have the same length.
mainKalmanPlot.py is running the same thing as mainKalman but collected velcoity data
for the old velocity algorithm vs the Kalman velcity correction. 
'''


'''
This code is for comparing velocities form kalman state matrix vs the past team's velocities calcs
Data is collected from running this and plotted in sep file

rod_x_asymptote_pixels[0] = 595
rod_x_asymptote_pixels[3] = 36
rod_x_asymptote_pixels[2] = 147
rod_x_asymptote_pixels[1] = 373

'''


import cv2
import numpy as np
import imutils
from math import sqrt
import time
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

pastVx = []
pastVy = []
kalmanVx = []
kalmanVy = []
yFinal = []
times = [] #for kalman vels 

pastTimes = []  #for the past teams vels calcs
motorDesiredData = []


def save_vel_data():
    data = {
        "pastVx": pastVx,
        "pastVy": pastVy,
        "kalmanVx":kalmanVx,
        "kalmanVy": kalmanVy,
        "times": times,
        "pastTimes": [x - start_time for x in timestamps],
        "yFinal": yFinal,
        "motorDesiredData": motorDesiredData
    }
    #print("Saving data...", data)  # Debugging output
    with open("kalman_vel_data.json", "w") as f:
        json.dump(data, f)

# Camera and distortion parameters
# defined parameters for calcualtions for removing distortion effects later
# K: intrinsic parameters of camera like focal length, principal point
# D: parameters to remove distortions, ex. if using fisheye lens
K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
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
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1  #initially .5  

# Initial state estimate
kalman.statePre = np.array([[0], [0], [0], [0]], np.float32)

# Initialize ball position
x2, y2 = 0, 0  # Predicted position
x, y = 0, 0  # Measured position from vision system

# Initialization of tracking and time measurement
x_coords, y_coords = [], [] #stores values for x and y positions for tracking
timestamps = [] #array to store time values 

# Dimensions of the table in inches
width_inches = 23.09
length_inches = 46.75
# Stepper motor response time (dummy values, in seconds)
v_stepper = 10

# Pixel coordinates of the table corners
ULCorner = (0, 0)  # Upper Left (194,134)
URCorner = (840, 0)  # Upper Right (1061, 136)
BLCorner = (0, 470)  # Bottom Left (200, 626)
BRCorner = (840, 470)  # Bottom Right (1066, 609)


# helper methods
# Convert player area positions from inches to pixels
# ppi is pixels per inch 
def convert_to_pixels(player_areas, ppi):
    return [(start * ppi + URCorner[1], end * ppi + URCorner[1]) for start, end in player_areas]


# Convert rod x-asymptotes from inches to pixels
def convert_rod_asymptotes(rod_asymptotes, ppi):
    return [x * ppi + ULCorner[0] for x in rod_asymptotes]

#normalizes the given y position to a value between 0 and 1 where 0 is at the top of the table and 1 is at the bottom of the table
def normalize_y_position(y, top_pixel=URCorner[1], bottom_pixel=BRCorner[1]):
    if y < top_pixel:
        return 0
    elif y > bottom_pixel:
        return 1
    else:
        return (y - top_pixel) / (bottom_pixel - top_pixel)


# Function to predict the final position of the ball based on current and previous positions
def predict_final_position(vx,vy,x,y):
    #x1, y1 are the second to last positions recorded
    #x2, y2 are the last recorded positions
    #timediff is the time between the last two recordings
    
    # if vx<1: vx = 0
    # if vy<1: vy = 0
    # print("vx",vx)
    x_final = np.array(rod_x_asymptote_pixels)

    if vx != 0:  #ball is not moving horizontally
        #y_final = (y + vy * (x_final - x) / vx).astype(int) #gives final y position for when ball is at x location for each rod, array
        y_final = (y + vy * (x_final - x) / vx)
        #print(y_final)
    else:
        # Create an array of y2 repeated for the length of x_final
        #y_final = np.full(x_final.shape, y,dtype=int)  #all the entries in y_final should be y2 for all x locations
        y_final = np.full(x_final.shape, y)

    pastVx.append(vx)
    pastVy.append(vy)

    #thresholding between +- 1 pixel
    if len(yFinal)>1:
        prev = yFinal[-1]
        prev = np.array(prev)
        #print("prev",prev)
        ymask = np.abs(y_final - prev) <= 2
        y_final[ymask] = prev[ymask]

        yFinal.append(y_final.tolist())
    else:
        yFinal.append(y_final.tolist())

    return x_final, y_final

def closeEnough(array1, val2, tol):
    # Convert inputs to numpy arrays
    val1 = np.array(array1)
    # Compute the absolute difference and check against the tolerance
    return abs(val1 - val2) < tol


# Calculate pixel-per-inch ratio
width_pixels = URCorner[0] - ULCorner[0]  # stupid axis, players don't move in this direction
length_pixels = BRCorner[1] - URCorner[1]  # axis players move on, direction rod shifts
ppi_width = width_pixels / width_inches
ppi_length = length_pixels / length_inches

# Define player areas per rod in inches
player_areas_per_rod_inches = [
    [(0, 7.4033), (7.4033, 14.8066), (14.8066, 22.2099)],
    [(0, 3.6445), (4.7865, 8.3435), (9.318, 12.9655), (13.9455, 17.969), (19.014, 23.09)],
    [(0, 12.551), (9.63, 22.195)],
    [(0, 8.3), (7.179, 15.479), (14.3, 22.575)]
]

# Rod x-asymptotes in inches
rod_x_asymptote_inches = [32.125, 20.5, 8.875, 3]

# Convert to pixels
#old teams
# player_areas_per_rod_pixels = [
#     [(19.5, 165), (165, 310.5), (305, 450.5)],
#     [(10, 85.5), (107, 182.5), (201, 276.5), (295, 370.5), (390, 465)],
#     [(12, 265), (207, 460)],
#     [(12, 178), (205.5, 371.5), (347, 513)]
# ]


# Convert to pixels
#4/11 new values
player_areas_per_rod_pixels = [
    [(10, 149), (149, 288), (288, 426)],
    [(12, 85), (104, 177), (195, 269), (286, 360), (376, 450)],
    [(11, 264), (202, 454)],
    [(14, 177), (160, 320), (302, 459)]
]


rod_x_asymptote_pixels = convert_rod_asymptotes(rod_x_asymptote_inches, ppi_width)

#old teams

# rod_x_asymptote_pixels[0] = 595
# rod_x_asymptote_pixels[3] = 36
# rod_x_asymptote_pixels[2] = 147
# rod_x_asymptote_pixels[1] = 373

# new 4/18

rod_x_asymptote_pixels[0] = 615
rod_x_asymptote_pixels[3] = 59
rod_x_asymptote_pixels[2] = 173
rod_x_asymptote_pixels[1] = 396

#print("Player Areas per Rod in Pixels:", player_areas_per_rod_pixels)
#print("Rod X-Asymptotes in Pixels:", rod_x_asymptote_pixels)

# Setup camera
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)


if not cap.isOpened():
    print("Error: Could not open video capture device.")
    exit()

# get everything ready for vision processing
# camera resolution: 1920x1080 pixels
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True) #used to detect moving object against static background

# current position of the ball (x2, y2 used for prediciton and x,y used for vision)
xCorrected, yCorrected = 0, 0  #prediction
x, y = 0, 0 #from vision system
x2,y2 = 0,0
x3,y3 = 0,0

# to mark location of ball in camera frame, (yellow circle that shows up on screen)
radius = 10

# Define range of orange color in HSV, for trakcing the orange ball
#lower_orange = np.array([0, 100, 100])
#upper_orange = np.array([100, 255, 255])


#Green ball threshold
lower_bound = np.array([65, 50, 85])
upper_bound = np.array([85, 110, 255])

# init communications change port as necessary
arduino = ArduinoCOM(port='COM3')  # Replace 'COM3' with your actual COM port

# init dummy values for coms arrays
motorCurrent = [0, 0, 0, 0]  #current stepper motor position
motorDesired = [0.5, 0.5, 0.5, 0.5] #desired stepper motor position
servoCurrent = [0, 0, 0, 0] #current servo motor position
servoDesired = [0, 0, 0, 0] #desired servo motor position
playerHitting = [-1, -1, -1, -1] #array to dicated which player on which of the four rods is hitting, initialized to all -1

# Track the start time, for dt in Kalman filter
prev_time = time.time()
start_time = prev_time 


# Main loop
while True:  #infinite loop to keep processing data
    # video processing
    
    ret, frame = cap.read()  #ret is bpolean for is feed is being captured, frame contains actual pixel data
    current_time = time.time() #records current time
    if not ret:
        print("Failed to grab frame")
        break
    frame = imutils.resize(frame, width=1200)  #resize frame, so whole table is shown after resolution change above
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
    frame = frame[120:590, 160:1000] #crops image to region of interest (table)
    #fgmask = fgbg.apply(frame) #applies background subtractor to get foreground mask to detect moving objects


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
            #x, y = int(x),int(y)
            # Calculate the time difference between frames
            current_time = time.time()
            #dt and elapsed time are the same AT FIRST ONLY
            elapsed_time = current_time-start_time
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
            vxCorrect, vyCorrect = corrected[2].item(), corrected[3].item()

            if abs(vxCorrect)<1: vxCorrect = 0
            if abs(vyCorrect)<1: vyCorrect = 0
            print("vx",vxCorrect)
            kalmanVx.append(vxCorrect)
            kalmanVy.append(vyCorrect)
            times.append(elapsed_time)
            

            # Draw visualization circles
            #cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)  # Red for measured
            #cv2.circle(frame, (int(x2), int(y2)), int(radius), (255, 0, 0), 2)  # Blue for predicted
            cv2.circle(frame, (int(x3), int(y3)), int(radius), (0, 255, 0), 2)  # Green for corrected


            #testing time array mismatch
            xCorrected, yCorrected = x3, y3  # Random values for testing
            x_coords.append(xCorrected) #add to x_coords array
            y_coords.append(yCorrected)
            timestamps.append(current_time) #log current time


        else:
        # Display "Ball Not Detected" if no contours found
            cv2.putText(frame, "Ball Not Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,  
                1, (0, 0, 255), 2, cv2.LINE_AA)
        
    if len(kalmanVx)>1:
            # Calculate velocity and predict final position
        # these velocities are thresholded
        vx = kalmanVx[-1]
        vy = kalmanVy[-1]
        x_final, y_final = predict_final_position(vx, vy, x3, y3)
        #print(type(yFinal))
        

        #returns final_x (all the rods positions), final_y (all the points at which it would be in y for the corrensponding x), vel_x, vel_y

        #enumeraing over (rod#, xposition of rod in pixels)
        for rod_index, x_rod in enumerate(rod_x_asymptote_pixels):
            time_to_intercept = np.abs((x_rod - x3) / vx) if vx != 0 else float('inf')
            #enumerate over all the player yranges for the specific rod (rod_index)
            #player_index is the player num (first player at top of rod in cam frame)
            #start and end indicates the y range for the player in rods span of motion
            for player_index, (start, end) in enumerate(player_areas_per_rod_pixels[rod_index]):
                #y_final is the y val the ball will be at when its xval = x_rod for that rod
                if start <= y_final[rod_index] <= end: #if y_final is inbetween range for that player
                    motor_travel_time = np.abs(
                        (normalize_y_position(y_final[rod_index]) - motorCurrent[rod_index]) / v_stepper)
                    if motor_travel_time <= time_to_intercept: #if time to travel is less that intercept time
                        stepper_position = (y_final[rod_index] - start) / (end - start) #normalized y position within player's range
                        hitInches = (end - start)*stepper_position + start 
                        # print(
                        #     f"Rod {rod_index + 1} Player {player_index + 1}: Move motor to position {stepper_position:.2f} to intercept")
                        motorDesired[rod_index] = 1-stepper_position  # update desired motor position array
                        playerHitting[rod_index] = player_index
                        #print("inside",motorDesired)
                    else:
                        # print(
                        #     f"Rod {rod_index + 1}: Cannot intercept in time, requires {motor_travel_time:.2f}s, available {time_to_intercept:.2f}s")
                        playerHitting[rod_index] = -1

        #print("outside",motorDesired)
        motorDesiredData.append(motorDesired.copy())
        #print(motorDesiredData)


        # servo stuff
        #print(rod_x_asymptote_pixels) #200, vvv, fff, 750
        #print(x2)  #current ball position in x?
        #rod_x_asymp pizel are the positions of all four rods in pixels
        #80 pixels is threshold
        servoDesired = closeEnough(rod_x_asymptote_pixels, x2, 40) #boolean array if each rod is close enough
        servoDesired = [float(value) for value in servoDesired]
        #print(servoDesired)


    # Display the result
    cv2.imshow('Kalman Filter Tracking', frame)

    # # set the values of x,y from vision to x2, y2 for prediction
    # #x2, y2 are the predicted values
    # xCorrected, yCorrected = x3, y3  # Random values for testing
    # x_coords.append(xCorrected) #add to x_coords array
    # y_coords.append(yCorrected)
    # timestamps.append(current_time) #log current time


        

    # send and receive coordinates via serial
    try:
        motorDesiredData.append(motorDesired)
        print(motorDesired)
        print()
        # Sending desired positions to the Arduino
        arduino.send_positions(motorDesired, servoDesired)
        #arduino.send_positions(motorDesired, [0,0,0,0])

        # Receiving and printing current positions from the Arduino
        motorCurrent, servoCurrent = arduino.receive_positions()

    except Exception as e:
         print("An error occurred:", e)

    end_time = time.time()
    #print(end_time-start_time)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #print("timestamps", len(timestamps))
        #pastTimes = [x - start_time for x in timestamps]
        #type(yFinal)
        save_vel_data()
        break

cap.release()
cv2.destroyAllWindows()