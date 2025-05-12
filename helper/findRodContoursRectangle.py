import cv2
import numpy as np
import imutils
from AntiFisheye import AntiFisheye
print(cv2.__version__)

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997],
              [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])  # Distortion coefficients

# HSV threshold for pink tape
lower_bound = np.array([150, 63, 130])
upper_bound = np.array([180, 140, 260])

# Video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    frame = frame[120:590, 160:1000]  # Crop to ROI

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    result1 = cv2.bitwise_and(frame, frame, mask=mask)

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    output_frame = frame.copy()

    # Get bounding rectangles for top 4 largest contours
    bounding_boxes = []
    if contours:
        # Sort contours by area descending
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours[:4]:  # Top 4
            if cv2.contourArea(c) > 100:
                x, y, w, h = cv2.boundingRect(c)
                bounding_boxes.append(((x, y), (x + w, y + h)))  # Top-left and bottom-right
                cv2.rectangle(output_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Print the bounding boxes' pixel coordinates
    if bounding_boxes:
        print("Top 4 Rectangular Regions (pixel coordinates):")
        for i, box in enumerate(bounding_boxes):
            print(f"Region {i + 1}: Top-left = {box[0]}, Bottom-right = {box[1]}")
    else:
        print("No valid contours found.")

    cv2.imshow("Original Frame", frame)
    cv2.imshow("Color Mask", result1)
    cv2.imshow("Output Frame", output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()