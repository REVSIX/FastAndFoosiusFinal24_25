import cv2
import numpy as np
import imutils
import time
import serial
import json
import subprocess
import sys
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

# --- Hardware detection for simulation mode --- #
camera_ok = False
arduino_ok = False

# Test camera
cap_test = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cap_test.isOpened():
    camera_ok = True
    cap_test.release()

# Test Arduino
try:
    arduino_test = ArduinoCOM(port='COM3')
    arduino_ok = True
    # optionally close until reopened later
except Exception:
    arduino_ok = False

if camera_ok and arduino_ok:
    mode = "FULL_REAL"
elif camera_ok:
    mode = "CAM_ONLY"
else:
    mode = "FULL_SIM"

# Launch FoosScope GUI in its own process
subprocess.Popen([sys.executable, "FoosScope.py", mode])

# --- (Your existing code begins here, unmodified) --- #
pastVx = []
pastVy = []
kalmanVx = []
kalmanVy = []
yFinal = []
times = []
frame_counter = 0
MAX_BUFFER = 25
send_every_n_frames = 1
pastTimes = []
motorDesiredData = []

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997],
              [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])
new_width = 800
scale_factor = new_width / 1200
K_scaled = K.copy()
K_scaled[0,0] *= scale_factor
K_scaled[1,1] *= scale_factor
K_scaled[0,2] *= scale_factor
K_scaled[1,2] *= scale_factor

kalman = cv2.KalmanFilter(4,2)
kalman.transitionMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], np.float32)
kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32)*0.03
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32)*0.1
kalman.statePre = np.zeros((4,1), dtype=np.float32)

x2,y2 = 0,0
x,y = 0,0
x_coords, y_coords = [], []
width_inches = 23.09
length_inches = 46.75
v_stepper = 10
ULCorner = (0,0)
URCorner = (570,0)
BLCorner = (0,325)
BRCorner = (570,325)

def normalize_y_position(y, top_pixel=URCorner[1], bottom_pixel=BRCorner[1]):
    if y < top_pixel: return 0
    elif y > bottom_pixel: return 1
    return (y - top_pixel)/(bottom_pixel - top_pixel)

def predict_final_position(vx,vy,x,y):
    x_final = np.array(rod_x_asymptote_pixels)
    if vx != 0:
        y_final = (y + vy*(x_final - x)/vx)
    else:
        y_final = np.full(x_final.shape, y)
    if len(yFinal)>1:
        prev = np.array(yFinal[-1])
        ymask = np.abs(y_final - prev) <= 2
        y_final[ymask] = prev[ymask]
        yFinal.append(y_final.tolist())
    else:
        yFinal.append(y_final.tolist())
    return x_final, y_final

def closeEnough(array1, val2, tol):
    return abs(np.array(array1) - val2) < tol

player_areas_per_rod_pixels = [
    [(19,112),(112,206),(206,297)],
    [(17,68),(80,131),(142,192),(202,251),(264,313)],
    [(18,185),(146,311)],
    [(23,127),(117,220),(211,314)]
]
rod_x_asymptote_pixels = [401,254,105,29]

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

# if camera_ok:
#     cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
#     cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
#     if not cap.isOpened():
#         print("Error: Could not open video capture device.")
#         exit()
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

xCorrected,yCorrected = 0,0
x3,y3 = 0,0
radius = 10
lower_bound = np.array([65,50,85])
upper_bound = np.array([85,110,255])
lower_bound_rod = np.array([160,63,185])
upper_bound_rod = np.array([180,123,260])
final_centers = []
uppercenter = [282,297,296,298]
lowercenter = [193,248,133,197]
arduino = None
if arduino_ok:
    arduino = ArduinoCOM(port='COM3')
motorCurrent = [0,0,0,0]
motorDesired = [0.5,0.5,0.5,0.5]
servoCurrent = [0,0,0,0]
servoDesired = [0,0,0,0]
playerHitting = [-1,-1,-1,-1]
final_centers_normalized=[0,0,0,0]
prev_time = time.time()
start_time = prev_time
lost_frames = 0
MAX_LOST=5
neutral_motor=[0.5,0.5,0.5,0.5]
neutral_servo=[0.0,0.0,0.0,0.0]

while True:
    frame_counter +=1
    ret = False
    if cap: ret, frame = cap.read()
    t0 = time.time()
    current_time = time.time()
    if cap and not ret:
        print("Failed to grab frame")
        break
    if cap:
        frame = imutils.resize(frame, width=new_width)
        frame = AntiFisheye.undistort_fisheye_image(frame, K_scaled, D)
        frame = frame[60:385,115:685]
    elapsed_time = current_time - start_time
    dt = current_time - prev_time
    prev_time = current_time
    kalman.transitionMatrix = np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]], np.float32)
    predicted = kalman.predict()
    x2, y2 = predicted[0].item(), predicted[1].item()
    vxpredicted, vypredicted = predicted[2].item(), predicted[3].item()
    vxCorrect, vyCorrect = vxpredicted, vypredicted
    if abs(vxCorrect)<1: vxCorrect=0
    if abs(vyCorrect)<1: vyCorrect=0
    x3, y3 = x2, y2

    if cap and frame_counter % send_every_n_frames == 0:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_rod = cv2.inRange(hsv, lower_bound_rod, upper_bound_rod)
        contours_rod = imutils.grab_contours(cv2.findContours(mask_rod, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))
        centers=[]
        if contours_rod:
            contours_rod = sorted(contours_rod, key=lambda c: cv2.contourArea(c), reverse=True)
            for c in contours_rod[:4]:
                if cv2.contourArea(c)>20:
                    x_,y_,w,h = cv2.boundingRect(c)
                    centers.append((x_+w//2, y_+h//2))
        if centers:
            final_centers = sorted(centers, key=lambda pt: pt[0], reverse=True)
            final_centersY = [c[1] for c in final_centers]
            final_centers_clipped = [max(min(num,uppercenter[i]),lowercenter[i]) for i,num in enumerate(final_centersY)]
            final_centers_normalized = [(uppercenter[i]-final_centers_clipped[i])/(uppercenter[i]-lowercenter[i]) for i in range(len(final_centers_clipped))]
        rodYNorm = [round(num,3) for num in final_centers_normalized] + [0.5]*(4-len(final_centers_normalized))
        motorCurrent = rodYNorm[:4]
        print("Rod update took", time.time()-t0, "motorCurrent", motorCurrent)

    if cap:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours = imutils.grab_contours(cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))
        if len(contours)>0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c)>50:
                lost_frames=0
                (x,y),_ = cv2.minEnclosingCircle(c)
                measurement = np.array([[np.float32(x)], [np.float32(y)]])
                corrected = kalman.correct(measurement)
                x3, y3 = corrected[0].item(), corrected[1].item()
                vxCorrect, vyCorrect = corrected[2].item(), corrected[3].item()
                if abs(vxCorrect)<1: vxCorrect=0
                if abs(vyCorrect)<1: vyCorrect=0
                cv2.circle(frame, (int(x3),int(y3)), radius, (0,255,0),2)
            else:
                lost_frames+=1
        print("Kalman took", time.time()-t0)

    xCorrected, yCorrected = x3, y3
    vx, vy = vxCorrect, vyCorrect
    x_final, y_final = predict_final_position(vx, vy, x3, y3)

    for rod_index, x_rod in enumerate(rod_x_asymptote_pixels):
        time_to_intercept = abs((x_rod-x3)/vx) if vx!=0 else float('inf')
        for player_index, (start,end) in enumerate(player_areas_per_rod_pixels[rod_index]):
            if start<=y_final[rod_index]<=end:
                motor_travel_time = abs((normalize_y_position(y_final[rod_index]) - motorCurrent[rod_index]) / v_stepper)
                if motor_travel_time <= time_to_intercept:
                    stepper_position=(y_final[rod_index]-start)/(end-start)
                    motorDesired[rod_index] = 1-stepper_position
                    playerHitting[rod_index] = player_index
                else:
                    playerHitting[rod_index] = -1

    servoDesired = [float(v) for v in closeEnough(rod_x_asymptote_pixels, x3, 40)]

    cv2.imshow('Kalman Filter Tracking', frame) if cap else None

    if frame_counter % send_every_n_frames ==0:
        try:
            if lost_frames>=MAX_LOST:
                motorDesired = neutral_motor[:]
                servoDesired = neutral_servo[:]
            if arduino_ok:
                arduino.send_positions(motorDesired, servoDesired)
                motorCurrent, servoCurrent = arduino.receive_positions()
            else:
                motorCurrent = motorDesired[:]
                servoCurrent = servoDesired[:]
        except Exception as e:
            print("An error occurred:", e)

    # Update shared GUI state
    # map camera output x3,y3 into GUI coordinate system
    # Example mapping for CAM_ONLY or FULL_REAL:
    # ballX_GUI = np.clip((x3 / 570) * TABLE_WIDTH, 0, TABLE_WIDTH)
    # ballY_GUI = np.clip((y3 / 325) * TABLE_HEIGHT, 0, TABLE_HEIGHT)
    # but since FoosScope reads directly, just update:
    try:
        from FoosScope import ball_pos, motor_pos, motor_target, servo_pos, servo_target
        ball_pos[0], ball_pos[1] = x3, y3
        motor_target[:] = motorDesired[:]
        servo_target[:] = servoDesired[:]
        motor_pos[:] = motorCurrent[:]
        servo_pos[:] = servoCurrent[:]
    except ImportError:
        pass

    if cv2.waitKey(1)&0xFF==ord('q'):
        break

if cap:
    cap.release()
cv2.destroyAllWindows()
