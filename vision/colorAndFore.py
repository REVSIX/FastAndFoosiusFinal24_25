## Applicaiton of both color and foreground mask 

import cv2
import numpy as np

# Define the lower and upper bounds for the HSV range, pink highlighter
#lower_bound = np.array([152, 157, 183])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([172, 217, 243])  # Upper bound of the range (Hue, Saturation, Value)

#widen range for pink highlighter
lower_bound = np.array([132, 137, 167])  # Lower bound of the range (Hue, Saturation, Value)
upper_bound = np.array([192, 237, 263])  # Upper bound of the range (Hue, Saturation, Value)

#orange glue cap
#lower_bound = np.array([163, 175, 147])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([183, 235, 207])  # Upper bound of the range (Hue, Saturation, Value)

#lower_bound = np.array([10, 100, 100])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([200, 255, 255])  # Upper bound of the range (Hue, Saturation, Value)

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
#fgbg = cv2.createBackgroundSubtractorKNN(detectShadows=False)


# Capture the video feed (or use an image)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    fgmask = fgbg.apply(frame)
    
    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the pink object within the defined HSV range
    # mask have frame with everything inRange in white and the rest in black
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound) 
    

    # Apply the mask to the original frame
    result1 = cv2.bitwise_and(frame, frame, mask=mask)
    result2 = cv2.bitwise_and(frame, frame, mask=fgmask)
    
    combinedMask = cv2.bitwise_and(mask,fgmask)
    result = cv2.bitwise_and(frame,frame,mask=combinedMask)


    # Show the original and the result with the mask applied
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Color Mask", result1)
    cv2.imshow("Foreground Mask",result2)
    cv2.imshow("Final Mask",result)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
