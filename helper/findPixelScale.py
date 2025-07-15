import cv2
import numpy as np
from AntiFisheye import AntiFisheye
import imutils

# Camera calibration parameters (example values)
K = np.array([
    [968.82202387, 0.0, 628.92706997],
    [0.0, 970.56156502, 385.82007021],
    [0.0, 0.0, 1.0]
])
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

new_width = 800

scale_factor = new_width / 1200 # e.g., 800 / 1200 = 0.6667
K_scaled = K.copy()
K_scaled[0, 0] *= scale_factor  # fx
K_scaled[1, 1] *= scale_factor  # fy
K_scaled[0, 2] *= scale_factor  # cx
K_scaled[1, 2] *= scale_factor  # cy

# Store clicked coordinates
clicked_coords = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked coordinates: x={x}, y={y}")
        clicked_coords.append((x, y))
        cv2.destroyAllWindows()

# Open webcam (DirectShow for Windows)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Set desired resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Capture a frame
ret, frame = cap.read()
cap.release()

if not ret or frame is None:
    print("Error: Failed to capture image from webcam.")
    exit()
else:
    print("Successfully captured frame.")

# Optional: Save raw frame to inspect if debugging
# cv2.imwrite("debug_raw_frame.jpg", frame)

# Safely resize
try:
    frame = imutils.resize(frame, width=new_width)
except Exception as e:
    print("Error resizing image:", e)
    exit()

# Apply fisheye correction
try:
    frame = AntiFisheye.undistort_fisheye_image(frame, K_scaled, D)
except Exception as e:
    print("Error during undistortion:", e)
    exit()

# Crop region of interest
try:
    frame = frame[60:385, 115:685]
except Exception as e:
    print("Error cropping image:", e)
    exit()

# Display image and handle mouse click
cv2.imshow("Captured Image - Click to Select Point", frame)
cv2.setMouseCallback("Captured Image - Click to Select Point", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()

# If user clicked, print result
if clicked_coords:
    print(f"Selected pixel: {clicked_coords[0]}")
else:
    print("No point selected.")
