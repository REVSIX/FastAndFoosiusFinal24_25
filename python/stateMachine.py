import cv2
import numpy as np
import imutils
import time
import serial
import json
from AntiFisheye import AntiFisheye
from ArduinoCOM import ArduinoCOM

# Camera and distortion parameters
K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
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

# Geometry helpers
def convert_to_pixels(player_areas, ppi):
    return [(start * ppi + URCorner[1], end * ppi + URCorner[1]) for start, end in player_areas]

def convert_rod_asymptotes(rod_asymptotes, ppi):
    return [x * ppi + ULCorner[0] for x in rod_asymptotes]

def normalize_y_position(y, top_pixel=URCorner[1], bottom_pixel=BRCorner[1]):
    return min(1, max(0, (y - top_pixel) / (bottom_pixel - top_pixel)))

def predict_final_position(x1, y1, x2, y2, time_diff):
    vx = (x2 - x1) / time_diff if time_diff > 0 else 0
    vy = (y2 - y1) / time_diff if time_diff > 0 else 0
    x_final = np.array(rod_x_asymptote_pixels)
    y_final = y2 + vy * (x_final - x2) / vx if vx != 0 else np.full_like(x_final, y2)
    return x_final, y_final, vx, vy

def closeEnough(array1, val2, tol):
    return abs(np.array(array1) - val2) < tol

# Pixels-per-inch and geometry setup
width_pixels = URCorner[0] - ULCorner[0]
length_pixels = BRCorner[1] - URCorner[1]
ppi_width = width_pixels / width_inches
ppi_length = length_pixels / length_inches

rod_x_asymptote_inches = [32.125, 20.5, 8.875, 3]
rod_x_asymptote_pixels = convert_rod_asymptotes(rod_x_asymptote_inches, ppi_width)
rod_x_asymptote_pixels = [595, 373, 147, 36]  # Overwrite with tuned values

player_areas_per_rod_pixels = [
    [(19.5, 165), (165, 310.5), (305, 450.5)],
    [(10, 85.5), (107, 182.5), (201, 276.5), (295, 370.5), (390, 465)],
    [(12, 265), (207, 460)],
    [(12, 178), (205.5, 371.5), (347, 513)]
]

# Color thresholds for tracking
lower_rgb = np.array([65, 50, 85])
upper_rgb = np.array([85, 110, 255])

# Arduino setup
arduino = ArduinoCOM(port='COM3')
motorCurrent = [0, 0, 0, 0]
motorDesired = [0.5, 0.5, 0.5, 0.5]
servoCurrent = [0, 0, 0, 0]
servoDesired = [0, 0, 0, 0]

# Foosball State Machine
class FoosballStateMachine:
    def __init__(self):
        self.state = "IDLE"
        self.controlled_rod = None
        self.controlled_player = None

    def update(self, x, y, vx, vy, x_final, y_final):
        if self.state == "IDLE":
            if abs(vy) > 2:
                self.state = "TRACKING"

        elif self.state == "TRACKING":
            rod_idx, player_idx = self.get_intercept_player(y_final, vy)
            if rod_idx is not None:
                self.controlled_rod = rod_idx
                self.controlled_player = player_idx
                self.state = "TRAPPING"

        elif self.state == "TRAPPING":
            if self.has_control_of_ball(y):
                if rod_idx in [2, 3]:
                    self.state = "PASSING"
                else:
                    self.state = "SHOOTING"

        elif self.state == "PASSING":
            self.state = "IDLE"  # Placeholder: implement pass logic

        elif self.state == "SHOOTING":
            self.state = "IDLE"  # Placeholder: implement shot logic

        return self.generate_motor_servo_commands(x_final, y_final)

    def get_intercept_player(self, y_final, vy):
        direction = -1 if vy < 0 else 1
        for rod_index, players in enumerate(player_areas_per_rod_pixels):
            for player_index, (start, end) in enumerate(players):
                if start <= y_final[rod_index] <= end:
                    return rod_index, player_index
        return None, None

    def has_control_of_ball(self, y):
        return 0 <= y <= 470

    def generate_motor_servo_commands(self, x_final, y_final):
        if self.controlled_rod is None or self.controlled_player is None:
            return motorDesired, servoDesired

        rod = self.controlled_rod
        player_area = player_areas_per_rod_pixels[rod][self.controlled_player]
        stepper_position = (y_final[rod] - player_area[0]) / (player_area[1] - player_area[0])
        motorDesired[rod] = 1 - stepper_position
        servoDesired[rod] = 1.0  # Example kick angle
        return motorDesired, servoDesired

# Initialize video
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

x, y, x2, y2 = 0, 0, 0, 0
radius = 10
state_machine = FoosballStateMachine()

while True:
    start_time = time.time()
    ret, frame = cap.read()
    current_time = time.time()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    frame = frame[120:590, 160:1000]
    fgmask = fgbg.apply(frame)
    mask = cv2.inRange(frame, lower_rgb, upper_rgb)
    combined_mask = cv2.bitwise_and(mask, fgmask)

    contours = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if contours:
        c = max(contours, key=cv2.contourArea)
        if 50 < cv2.contourArea(c) < 5000:
            ((x, y), _) = cv2.minEnclosingCircle(c)

    x2, y2 = x, y
    x_coords.append(x2)
    y_coords.append(y2)
    timestamps.append(current_time)

    if len(x_coords) > 1:
        time_diff = timestamps[-1] - timestamps[-2]
        x_final, y_final, vx, vy = predict_final_position(x_coords[-2], y_coords[-2], x_coords[-1], y_coords[-1], time_diff)
        motorDesired, servoDesired = state_machine.update(x2, y2, vx, vy, x_final, y_final)

    try:
        arduino.send_positions(motorDesired, servoDesired)
        motorCurrent, servoCurrent = arduino.receive_positions()
    except Exception as e:
        print("Arduino Error:", e)

    cv2.circle(frame, (int(x2), int(y2)), int(radius), (0, 255, 255), 2)
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
