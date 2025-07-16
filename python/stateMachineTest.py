import numpy as np
import time
import cv2
import imutils

# Camera-based foosball state simulation
rod_x_asymptote_pixels = [595, 373, 147, 36]
player_areas_per_rod_pixels = [
    [(19.5, 165), (165, 310.5), (305, 450.5)],
    [(10, 85.5), (107, 182.5), (201, 276.5), (295, 370.5), (390, 465)],
    [(12, 265), (207, 460)],
    [(12, 178), (205.5, 371.5), (347, 513)]
]

# HSV range for green (was misnamed orange)
lower_green = np.array([65, 50, 85])
upper_green = np.array([85, 110, 255])

class FoosballStateMachine:
    def __init__(self):
        self.state = "IDLE"
        self.controlled_rod = None
        self.controlled_player = None

    def update(self, x, y, vx, vy, x_final, y_final):
        print(f"\nCurrent State: {self.state}")

        if self.state == "IDLE":
            if abs(vy) > 2:
                print("Transition: IDLE -> TRACKING")
                self.state = "TRACKING"

        elif self.state == "TRACKING":
            rod_idx, player_idx = self.get_intercept_player(y_final, vy)
            if rod_idx is not None:
                self.controlled_rod = rod_idx
                self.controlled_player = player_idx
                print(f"Tracking ball to Rod {rod_idx}, Player {player_idx}")
                print("Transition: TRACKING -> TRAPPING")
                self.state = "TRAPPING"

        elif self.state == "TRAPPING":
            if self.has_control_of_ball(y):
                if self.controlled_rod in [2, 3]:
                    print("Trapped! Transition: TRAPPING -> PASSING")
                    self.state = "PASSING"
                else:
                    print("Trapped! Transition: TRAPPING -> SHOOTING")
                    self.state = "SHOOTING"

        elif self.state == "PASSING":
            print("Passing...")
            time.sleep(0.5)
            print("Pass complete. Transition: PASSING -> IDLE")
            self.state = "IDLE"

        elif self.state == "SHOOTING":
            print("Shooting...")
            time.sleep(0.5)
            print("Goal attempt made. Transition: SHOOTING -> IDLE")
            self.state = "IDLE"

    def get_intercept_player(self, y_final, vy):
        for rod_index, players in enumerate(player_areas_per_rod_pixels):
            for player_index, (start, end) in enumerate(players):
                if start <= y_final[rod_index] <= end:
                    return rod_index, player_index
        return None, None

    def has_control_of_ball(self, y):
        return 0 <= y <= 470

def predict_final_position(x1, y1, x2, y2, time_diff):
    vx = (x2 - x1) / time_diff if time_diff > 0 else 0
    vy = (y2 - y1) / time_diff if time_diff > 0 else 0
    x_final = np.array(rod_x_asymptote_pixels)
    y_final = y2 + vy * (x_final - x2) / vx if vx != 0 else np.full_like(x_final, y2)
    return x_final, y_final, vx, vy

# Initialize state machine
state_machine = FoosballStateMachine()

# Camera setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

x_coords, y_coords, timestamps = [], [], []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)
    frame = frame[120:590, 160:1000]

    mask = cv2.inRange(frame, lower_rgb, upper_rgb)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if contours:
        c = max(contours, key=cv2.contourArea)
        if 50 < cv2.contourArea(c) < 5000:
            ((x, y), _) = cv2.minEnclosingCircle(c)
            x_coords.append(x)
            y_coords.append(y)
            timestamps.append(time.time())

            if len(x_coords) > 1:
                time_diff = timestamps[-1] - timestamps[-2]
                x_final, y_final, vx, vy = predict_final_position(
                    x_coords[-2], y_coords[-2], x_coords[-1], y_coords[-1], time_diff)
                print(f"Ball at ({x:.1f}, {y:.1f}) | vx: {vx:.2f}, vy: {vy:.2f}")
                state_machine.update(x, y, vx, vy, x_final, y_final)

            cv2.circle(frame, (int(x), int(y)), 10, (0, 255, 255), 2)

    cv2.imshow("State Debug View", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
