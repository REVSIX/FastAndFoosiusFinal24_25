import cv2
import numpy as np
import imutils
from AntiFisheye import AntiFisheye
print(cv2.__version__)

K = np.array([[968.82202387, 0.00000000e+00, 628.92706997], [0.00000000e+00, 970.56156502, 385.82007021],
              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # Example camera matrix
D = np.array([-0.04508764, -0.01990902, 0.08263842, -0.0700435])

# Define the lower and upper bounds for the HSV range, pink highlighter
#lower_bound = np.array([152, 157, 183])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([172, 217, 243])  # Upper bound of the range (Hue, Saturation, Value)

#widen range for pink highlighter
#lower_bound = np.array([132, 137, 167])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([192, 237, 263])  # Upper bound of the range (Hue, Saturation, Value)

#orange glue cap
#lower_bound = np.array([163, 175, 147])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([183, 235, 207])  # Upper bound of the range (Hue, Saturation, Value)

#lower_bound = np.array([10, 100, 100])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([200, 255, 255])  # Upper bound of the range (Hue, Saturation, Value)

# testing pink ball on table
#lower_bound = np.array([157, 84, 223])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([177, 144, 283])  # Upper bound of the range (Hue, Saturation, Value)

#prev teams thresholds
#lower_bound = np.array([0, 100, 100])
#upper_bound = np.array([100, 255, 255])

#green ball threshold
lower_bound = np.array([65, 50, 85])
upper_bound = np.array([85, 110, 255])

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
#fgbg = cv2.createBackgroundSubtractorKNN(detectShadows=False)


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

    fgmask = fgbg.apply(frame)
    
    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the pink object within the defined HSV range
    # mask have frame with everything inRange in white and the rest in black
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound) 
    

    # Apply the mask to the original frame
    result1 = cv2.bitwise_and(frame, frame, mask=mask)
    result2 = cv2.bitwise_and(frame, frame, mask=fgmask)
    
    combinedMask = cv2.bitwise_and(mask,fgmask)  #oombine the two masks
    #_, combinedMask = cv2.threshold(combinedMask, 127, 255, cv2.THRESH_BINARY)
    result = cv2.bitwise_and(frame,frame,mask=combinedMask) #apply combined mask to frame


    # Assuming 'combined_mask' is the binary mask image
    #check if can be changed to combinedMASk at foosball table
    contours = cv2.findContours(combinedMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
    cv2.imshow("Foreground Mask",result2)
    #cv2.imshow("Final Mask",result)
    cv2.imshow("Combined Mask",combinedMask)
    cv2.imshow("Output Frame",output_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
