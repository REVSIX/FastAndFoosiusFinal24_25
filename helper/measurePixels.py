import cv2
import numpy as np
import math

# Global variables to store mouse clicks
center = None
edge = None
drawing = False

def mouse_callback(event, x, y, flags, param):
    global center, edge, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        center = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        edge = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        edge = (x, y)
        drawing = False

# Step 1: Capture image from webcam
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


print("Press SPACE to capture image...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Live Camera - Press SPACE to capture", frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        captured_image = frame.copy()
        break

cap.release()
cv2.destroyAllWindows()

# Step 2: Show image and let user select circular region
clone = captured_image.copy()
cv2.namedWindow("Select Circular ROI - Click center and drag")
cv2.setMouseCallback("Select Circular ROI - Click center and drag", mouse_callback)

while True:
    display = clone.copy()
    if center and edge:
        radius = int(math.hypot(edge[0] - center[0], edge[1] - center[1]))
        cv2.circle(display, center, radius, (0, 255, 0), 2)

    cv2.imshow("Select Circular ROI - Click center and drag", display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# Step 3: Calculate pixel count in the selected circle
if center and edge:
    mask = np.zeros(captured_image.shape[:2], dtype=np.uint8)
    radius = int(math.hypot(edge[0] - center[0], edge[1] - center[1]))
    cv2.circle(mask, center, radius, 255, -1)  # Fill the circle

    pixel_count = cv2.countNonZero(mask)
    diameter = 2 * radius

    print(f"\n🟢 Circle Selected:")
    print(f" - Radius: {radius} pixels")
    print(f" - Diameter: {diameter} pixels")
    print(f" - Pixels inside circle: {pixel_count}")
else:
    print("No circle was selected.")
