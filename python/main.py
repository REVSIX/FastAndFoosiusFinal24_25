import cv2
import numpy as np
import imutils
import time
import serial
from AntiFisheye import AntiFisheye

# === CONFIGURATION ===
K = np.array([[968.82202387, 0.0, 628.92706997], [0.0, 970.56156502, 385.82007021], [0.0, 0.0, 1.0]])
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

width_inches = 23.09
length_inches = 46.75
v_stepper = 10

ULCorner, URCorner = (0, 0), (840, 0)
BLCorner, BRCorner = (0, 470), (840, 470)

# === FUNCTIONS ===
def convert_rod_asymptotes(rod_asymptotes, ppi):
    return [x * ppi + ULCorner[0] for x in rod_asymptotes]

def normalize_y_position(y, top_pixel=URCorner[1], bottom_pixel=BRCorner[1]):
    return min(max((y - top_pixel) / (bottom_pixel - top_pixel), 0), 1)

def predict_final_position(x1, y1, x2, y2, time_diff):
    vx = (x2 - x1) / time_diff if time_diff > 0 else 0
    vy = (y2 - y1) / time_diff if time_diff > 0 else 0
    x_final = np.array(rod_x_asymptote_pixels)
    y_final = y2 + vy * (x_final - x2) / vx if vx != 0 else np.full_like(x_final, y2)
    return x_final, y_final, vx, vy

def closeEnough(array1, val2, tol):
    return abs(np.array(array1) - val2) < tol

def send_trap_command(arduino_serial):
    try:
        print("Sending trap command...")
        arduino_serial.write(b"trap\n")
        time.sleep(0.5)
    except Exception as e:
        print("Failed to send trap command:", e)

# === INIT ===
rod_x_asymptote_inches = [32.125, 20.5, 8.875, 3]
ppi_width = (URCorner[0] - ULCorner[0]) / width_inches
rod_x_asymptote_pixels = convert_rod_asymptotes(rod_x_asymptote_inches, ppi_width)
rod_x_asymptote_pixels = [595, 373, 147, 36]  # overrides

player_areas_per_rod_pixels = [
    [(19.5, 165), (165, 310.5), (305, 450.5)],
    [(10, 85.5), (107, 182.5), (201, 276.5), (295, 370.5), (390, 465)],
    [(12, 265), (207, 460)],
    [(12, 178), (205.5, 371.5), (347, 513)]
]

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Camera not detected.")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

x_coords, y_coords, timestamps = [], [], []
x2, y2 = 0, 0
x, y = 0, 0
radius = 10
lower_orange = np.array([0, 100, 100])
upper_orange = np.array([100, 255, 255])

arduino = serial.Serial('COM4', 9600)
time.sleep(2)  # Wait for Arduino to initialize

motorCurrent = [0, 0, 0, 0]
motorDesired = [0.5, 0.5, 0.5, 0.5]
servoDesired = [0, 0, 0, 0]
trapFlags = [False, False, False, False]
trapReady = [True, True, True, True]

# === MAIN LOOP ===
while True:
    ret, frame = cap.read()
    current_time = time.time()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    frame = frame[120:590, 160:1000]
    fgmask = fgbg.apply(frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    combined_mask = cv2.bitwise_and(mask, fgmask)
    contours = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            ((x, y), _) = cv2.minEnclosingCircle(c)

    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
    cv2.imshow('Frame', frame)

    x2, y2 = x, y
    x_coords.append(x2)
    y_coords.append(y2)
    timestamps.append(current_time)

    if len(x_coords) > 1:
        time_diff = timestamps[-1] - timestamps[-2]
        x_final, y_final, vx, vy = predict_final_position(
            x_coords[-2], y_coords[-2], x_coords[-1], y_coords[-1], time_diff)

        for rod_index, x_rod in enumerate(rod_x_asymptote_pixels):
            time_to_intercept = np.abs((x_rod - y2) / vx) if vx != 0 else float('inf')
            for player_index, (start, end) in enumerate(player_areas_per_rod_pixels[rod_index]):
                if start <= y_final[rod_index] <= end:
                    motor_travel_time = np.abs(
                        (normalize_y_position(y_final[rod_index]) - motorCurrent[rod_index]) / v_stepper)
                    if motor_travel_time <= time_to_intercept:
                        stepper_position = (y_final[rod_index] - start) / (end - start)
                        motorDesired[rod_index] = 1 - stepper_position
                        trapFlags[rod_index] = True
                    else:
                        trapFlags[rod_index] = False

        servoDesired = closeEnough(rod_x_asymptote_pixels, x2, 80)
        servoDesired = [float(val) for val in servoDesired]

        # Trap logic
        for rod_index, trap in enumerate(trapFlags):
            if trap and trapReady[rod_index]:
                send_trap_command(arduino)
                trapReady[rod_index] = False

            # Reset if ball far away from rod
            if abs(x2 - rod_x_asymptote_pixels[rod_index]) > 120:
                trapReady[rod_index] = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()