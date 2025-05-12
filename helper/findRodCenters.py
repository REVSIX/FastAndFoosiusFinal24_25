import cv2
import numpy as np
import imutils
from AntiFisheye import AntiFisheye
print(cv2.__version__)

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997],
              [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

lower_bound = np.array([160, 63, 185])
upper_bound = np.array([180, 123, 260])

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

final_centers = []  # Store results from the last frame

uppercenter = [390, 412, 410, 416] #upper bounds of the center of the pink tape per rod
lowercenter = [255, 341, 168, 264]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D)
    #frame = imutils.resize(frame, width=840)
    frame = frame[120:590, 160:1000]

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    result1 = cv2.bitwise_and(frame, frame, mask=mask)

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    output_frame = frame.copy()
    centers = []

    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours[:4]:
            if cv2.contourArea(c) > 50:
                x, y, w, h = cv2.boundingRect(c)
                center_x = x + w // 2
                center_y = y + h // 2
                centers.append((center_x, center_y))
                cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(output_frame, (center_x, center_y), 5, (255, 0, 0), -1)

    if centers:
        print("number of large contours", len(centers))
        print("Top 4 Rectangular Region Centers (pixel coordinates):")
        for i, center in enumerate(centers):
            print(f"Region {i + 1}: Center = {center}")
        final_centers = centers  # Save the latest valid centers
    else:
        print("No valid contours found.")

    cv2.imshow("Original Frame", frame)
    cv2.imshow("Color Mask", result1)
    cv2.imshow("Output Frame", output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Return the final list of center coordinates from the last valid frame
final_centers = sorted(final_centers, key=lambda pt: pt[0], reverse=True)
final_centersY = [center[1] for center in final_centers]

final_centers_clipped = [max(min(num,uppercenter[i]),lowercenter[i]) for i, num in enumerate(final_centersY)]
final_centers_normalized = [(uppercenter[i]-final_centers_clipped[i])/(uppercenter[i]-lowercenter[i]) for i in range(len(final_centers_clipped)) ]

rodYNorm = [round(num,3) for num in final_centers_normalized]
rodYNorm += [.5]*(4-len(rodYNorm))

motorCurrent = rodYNorm[:4]
print("\nFinal Returned Centers:", final_centers)
print("\nFinal Normalized Motor Current:", motorCurrent)
