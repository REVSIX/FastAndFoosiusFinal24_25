import cv2
import numpy as np
import imutils
from math import sqrt
import time
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

# Camera and distortion parameters
K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

x_coords, y_coords = [], []
timestamps = []

width_inches = 23.09
length_inches = 46.75
v_stepper = 10

ULCorner = (0, 0)
URCorner = (840, 0)
BLCorner = (0, 470)
BRCorner = (840, 470)

def convert_to_pixels(player_areas, ppi):
    return [(start * ppi + URCorner[1], end * ppi + URCorner[1]) for start, end in player_areas]

def convert_rod_asymptotes(rod_asymptotes, ppi):
    return [x * ppi + ULCorner[0] for x in rod_asymptotes]

def normalize_y_position(y, top_pixel=URCorner[1], bottom_pixel=BRCorner[1]):
    if y < top_pixel:
        return 0
    elif y > bottom_pixel:
        return 1
    else:
        return (y - top_pixel) / (bottom_pixel - top_pixel)

def predict_final_position(x1, y1, x2, y2, time_diff):
    vx = (x2 - x1) / time_diff if time_diff > 0 else 0
    vy = (y2 - y1) / time_diff if time_diff > 0 else 0
    x_final = np.array(rod_x_asymptote_pixels)
    if vx != 0:
        y_final = y2 + vy * (x_final - x2) / vx
    else:
        y_final = np.full_like(x_final, y2)
    return x_final, y_final, vx, vy

def closeEnough(array1, val2, tol):
    val1 = np.array(array1)
    return abs(val1 - val2) < tol

width_pixels = URCorner[0] - ULCorner[0]
length_pixels = BRCorner[1] - URCorner[1]
ppi_width = width_pixels / width_inches
ppi_length = length_pixels / length_inches

player_areas_per_rod_inches = [
    [(0, 7.4033), (7.4033, 14.8066), (14.8066, 22.2099)],
    [(0, 3.6445), (4.7865, 8.3435), (9.318, 12.9655), (13.9455, 17.969), (19.014, 23.09)],
    [(0, 12.551), (9.63, 22.195)],
    [(0, 8.3), (7.179, 15.479), (14.3, 22.575)]
]

rod_x_asymptote_inches = [32.125, 20.5, 8.875, 3]

player_areas_per_rod_pixels = [
    [(19.5, 165), (165, 310.5), (305, 450.5)],
    [(10, 85.5), (107, 182.5), (201, 276.5), (295, 370.5), (390, 465)],
    [(12, 265), (207, 460)],
    [(12, 178), (205.5, 371.5), (347, 513)]
]
rod_x_asymptote_pixels = convert_rod_asymptotes(rod_x_asymptote_inches, ppi_width)
rod_x_asymptote_pixels[0] = 595
rod_x_asymptote_pixels[3] = 36
rod_x_asymptote_pixels[2] = 147
rod_x_asymptote_pixels[1] = 373

print("Player Areas per Rod in Pixels:", player_areas_per_rod_pixels)
print("Rod X-Asymptotes in Pixels:", rod_x_asymptote_pixels)

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open video capture device.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

x2, y2 = 0, 0
x, y = 0, 0

radius = 10

# ----------- CHANGED: Use BGR bounds for color tracking -----------
# For a yellow-green ball, RGB (204, 255, 110) is BGR (110, 255, 204)
lower_rgb = np.array([65, 50, 85])
upper_rgb = np.array([85, 110, 255])

# -----------------------------------------------------------------

arduino = ArduinoCOM(port='COM3')

motorCurrent = [0, 0, 0, 0]
motorDesired = [0.5, 0.5, 0.5, 0.5]
servoCurrent = [0, 0, 0, 0]
servoDesired = [0, 0, 0, 0]
playerHitting = [-1, -1, -1, -1]

while True:
    start_time = time.time()
    ret, frame = cap.read()
    current_time = time.time()
    if not ret:
        print("Failed to grab frame")
        break
    frame = imutils.resize(frame, width=1200)
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    frame = frame[120:590, 160:1000]
    fgmask = fgbg.apply(frame)

    # ----------- CHANGED: Use BGR for color tracking -----------
    # No need to convert to HSV; use frame directly
    mask = cv2.inRange(frame, lower_rgb, upper_rgb)
    # -----------------------------------------------------------

    combined_mask = cv2.bitwise_and(mask, fgmask)
    contours = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 50 and cv2.contourArea(c) > 500:
            ((x, y), _) = cv2.minEnclosingCircle(c)

    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
    cv2.imshow('Frame', frame)

    x2, y2 = x, y
    x_coords.append(x2)
    y_coords.append(y2)
    timestamps.append(current_time)

    if len(x_coords) > 1:
        time_diff = timestamps[-1] - timestamps[-2]
        x_final, y_final, vx, vy = predict_final_position(x_coords[-2], y_coords[-2], x_coords[-1], y_coords[-1], time_diff)

        for rod_index, x_rod in enumerate(rod_x_asymptote_pixels):
            time_to_intercept = np.abs((x_rod - y2) / vx) if vx != 0 else float('inf')
            for player_index, (start, end) in enumerate(player_areas_per_rod_pixels[rod_index]):
                if start <= y_final[rod_index] <= end:
                    motor_travel_time = np.abs(
                        (normalize_y_position(y_final[rod_index]) - motorCurrent[rod_index]) / v_stepper)
                    if motor_travel_time <= time_to_intercept:
                        stepper_position = (y_final[rod_index] - start) / (end - start)
                        hitInches = (end - start)*stepper_position + start
                        print(
                            f"Rod {rod_index + 1} Player {player_index + 1}: Move motor to position {stepper_position:.2f} to intercept")
                        motorDesired[rod_index] = 1-stepper_position
                        playerHitting[rod_index] = player_index
                    else:
                        print(
                            f"Rod {rod_index + 1}: Cannot intercept in time, requires {motor_travel_time:.2f}s, available {time_to_intercept:.2f}s")
                        playerHitting[rod_index] = -1
        print(x2)
        servoDesired = closeEnough(rod_x_asymptote_pixels, x2, 80)
        servoDesired = [float(value) for value in servoDesired]
        print(servoDesired)

    try:
        arduino.send_positions(motorDesired, servoDesired)
        motorCurrent, servoCurrent = arduino.receive_positions()
    except Exception as e:
        print("An error occurred:", e)

    end_time = time.time()
    print(end_time-start_time)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
