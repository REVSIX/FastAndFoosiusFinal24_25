import cv2
import numpy as np

# Initialize the camera
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# Capture a frame
ret, frame = camera.read()
if not ret:
    print("Error: Could not capture frame.")
    camera.release()
    exit()

# Convert to HSV
hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Select the ROI
roi = cv2.selectROI("Select Object", frame)
cv2.destroyAllWindows()

# Crop the ROI from the HSV image
x, y, w, h = roi
object_roi = hsv_image[y:y+h, x:x+w]

# Calculate the average HSV value of the object
average_hsv = np.mean(object_roi, axis=(0, 1))
print(f"Average HSV of the selected object: {average_hsv}")

# Optionally, inspect a specific pixel
pixel_hsv = object_roi[0, 0]
print(f"HSV value of the top-left pixel: {pixel_hsv}")

# Release the camera
camera.release()
cv2.destroyAllWindows()


# import cv2
# import numpy as np
# import imutils
# from AntiFisheye import AntiFisheye

# # Initialize the camera
# #camera = cv2.VideoCapture(0)

# K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
#               [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
# D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

# camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


# if not camera.isOpened():
#     print("Error: Could not open camera.")
#     exit()

# # Capture a frame
# ret, frame = camera.read()
# frame = imutils.resize(frame, width=1200)  #resize frame, so whole table is shown after resolution change
# frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
# frame = frame[120:590, 160:1000] #crops image to region of interest (table)

# if not ret:
#     print("Error: Could not capture frame.")
#     camera.release()
#     exit()

# # Convert to HSV
# hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# # Select the ROI
# roi = cv2.selectROI("Select Object", frame)
# cv2.destroyAllWindows()

# # Crop the ROI from the HSV image
# x, y, w, h = roi
# object_roi = hsv_image[y:y+h, x:x+w]

# # Calculate the average HSV value of the object
# average_hsv = np.mean(object_roi, axis=(0, 1))
# print(f"Average HSV of the selected object: {average_hsv}")

# # Optionally, inspect a specific pixel
# pixel_hsv = object_roi[0, 0]
# print(f"HSV value of the top-left pixel: {pixel_hsv}")

# # Convert the average HSV back to BGR for visualization
# average_bgr = cv2.cvtColor(np.uint8([[average_hsv]]), cv2.COLOR_HSV2BGR)[0][0]
# print(f"Average BGR of the selected object: {average_bgr}")

# # Show the original ROI in BGR
# cv2.imshow("Selected Object (BGR)", frame[y:y+h, x:x+w])
# cv2.waitKey(0)

# # Release the camera
# camera.release()
# cv2.destroyAllWindows()

