import cv2
import numpy as np
import imutils
from AntiFisheye import AntiFisheye

# Define the lower and upper bounds for the HSV range, pink highlighter
#lower_bound = np.array([152, 157, 187])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([172, 217, 243])  # Upper bound of the range (Hue, Saturation, Value)


#orange glue cap
#lower_bound = np.array([163, 175, 147])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([183, 235, 207])  # Upper bound of the range (Hue, Saturation, Value)

#pink highlighter
#lower_bound = np.array([10, 100, 100])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([200, 255, 255])  # Upper bound of the range (Hue, Saturation, Value)


## testing pink ball on table
#lower_bound = np.array([157, 84, 223])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([177, 144, 283])  # Upper bound of the range (Hue, Saturation, Value)

#prev teams thresholds
#lower_bound = np.array([0, 100, 100])
#upper_bound = np.array([100, 255, 255])

#green ball threshold
lower_bound = np.array([65, 50, 85])
upper_bound = np.array([85, 110, 255])


# Capture the video feed (or use an image)
#cap = cv2.VideoCapture(0)

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=1200)  #resize frame, so whole table is shown after resolution change
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
    frame = frame[120:590, 160:1000] #crops image to region of interest (table)
    if not ret:
        break

    
    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the pink object within the defined HSV range
    # mask have frame with everything inRange in white and the rest in black
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound) 
    

    # Apply the mask to the original frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Show the original and the result with the mask applied
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Masked Frame", result)
    #cv2.imshow("Mask",mask)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
