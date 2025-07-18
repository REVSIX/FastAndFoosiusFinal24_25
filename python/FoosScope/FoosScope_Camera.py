import numpy as np
import time
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
from threading import Thread

# --- GUI Setup --- #
table_width = 800
table_height = 480

ball_position = [table_width // 2, table_height // 2]
latest_position = [table_width // 2, table_height // 2]
latest_frame = np.zeros((360, 640, 3), dtype=np.uint8)

fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Foosball Table Live Tracker")
ax.set_xlim(0, table_width)
ax.set_ylim(0, table_height)
ax.set_aspect('equal')
ax.set_facecolor("forestgreen")
ax.invert_yaxis()

# Draw the table border
table_border = Rectangle((0, 0), table_width, table_height, linewidth=3, edgecolor='white', facecolor='none')
ax.add_patch(table_border)

# Draw the ball
ball = Circle((ball_position[0], ball_position[1]), radius=10, color='white')
ax.add_patch(ball)

# --- Camera Tracking Thread --- #
def track_ball():
    global latest_position, latest_frame
    lower_green = np.array([65, 50, 85])
    upper_green = np.array([85, 110, 255])

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (1200, int(frame.shape[0] * 1200 / frame.shape[1])))
        cropped = frame[120:590, 160:1000]
        display_frame = cropped.copy()

        fgmask = fgbg.apply(cropped)
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        combined_mask = cv2.bitwise_and(mask, fgmask)
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 500:
                ((x, y), _) = cv2.minEnclosingCircle(c)
                gui_x = np.clip((x / 840) * table_width, 0, table_width)
                gui_y = np.clip((y / 470) * table_height, 0, table_height)
                latest_position[0] = gui_x
                latest_position[1] = gui_y

                # Fixed-size circle to match GUI ball size
                center = (int(x), int(y))
                cv2.circle(display_frame, center, 10, (0, 255, 0), 2)


        # Resize for showing
        latest_frame = cv2.resize(display_frame, (640, 360))
        cv2.imshow("Foosball Camera Feed", latest_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start camera tracking in separate thread
camera_thread = Thread(target=track_ball, daemon=True)
camera_thread.start()

# --- Animation Update Function --- #
def update_gui(frame):
    ball.set_center((latest_position[0], latest_position[1]))
    return ball,

# Start animation
ani = FuncAnimation(fig, update_gui, interval=30, blit=True)
plt.show()
