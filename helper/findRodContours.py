import cv2
import numpy as np
import imutils
from AntiFisheye import AntiFisheye
print(cv2.__version__)

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])


#pink tape threshold
#lower_bound = np.array([160, 63, 185])
#upper_bound = np.array([180, 123, 260])



#5/9
#pink tape
lower_bound = np.array([150, 63, 130])
upper_bound = np.array([180, 140, 260])


## light blue tape
#lower_bound = np.array([100, 100, 220])
#upper_bound = np.array([120, 160, 280])

# purple tape
# lower_bound = np.array([120, 143, 112])
# upper_bound = np.array([140, 203, 172])


# Capture the video feed (or use an image)
#cap = cv2.VideoCapture(0) #laptop camera
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=1200)  #resize frame, so whole table is shown after resolution change
    frame = AntiFisheye.undistort_fisheye_image(frame, K, D) #anti-fisheye
    frame = frame[120:590, 160:1000] #crops image to region of interest (table)
    
    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the pink object within the defined HSV range
    # mask have frame with everything inRange in white and the rest in black
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound) 

    result1 = cv2.bitwise_and(frame, frame, mask=mask)
    
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    print(contours)
    

    # Create a copy of the original frame to draw contours on
    output_frame = frame.copy()
    x,y = 0,0
    # Check if contours are detected and then draw them
    if len(contours) > 0:
        cv2.drawContours(output_frame, contours, -1, (0, 255, 0), 2)  # Green color, thickness 2
        c = max(contours, key=cv2.contourArea) #select largest contour based on the area of the detected contours
        if cv2.contourArea(c) > 50 and cv2.contourArea(c) > 500:  # Update this threshold as needed
            ((x, y), _) = cv2.minEnclosingCircle(c) #gets the minimum enclosing circle around the object, x and y set to center of the yellow circle
    else:
        print("No contours found")

    cv2.circle(output_frame, (int(x), int(y)), int(10), (0, 255, 255), 2) 


    # Show the original and the result with the mask applied
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Color Mask", result1)
    cv2.imshow("Output Frame",output_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
