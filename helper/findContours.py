import cv2
import numpy as np
import imutils
print(cv2.__version__)
# Define the lower and upper bounds for the HSV range, pink highlighter
#lower_bound = np.array([152, 157, 183])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([172, 217, 243])  # Upper bound of the range (Hue, Saturation, Value)

#widen range for pink highlighter
lower_bound = np.array([132, 137, 167])  # Lower bound of the range (Hue, Saturation, Value)
upper_bound = np.array([192, 237, 263])  # Upper bound of the range (Hue, Saturation, Value)

#green ping pong ball
# lower_bound = np.array([65, 50, 85])
# upper_bound = np.array([85, 110, 255])

#green ping pong ball - carr library
lower_bound = np.array([48, 45, 203])
upper_bound = np.array([68, 105, 263])

#orange glue cap
#lower_bound = np.array([163, 175, 147])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([183, 235, 207])  # Upper bound of the range (Hue, Saturation, Value)

#lower_bound = np.array([10, 100, 100])  # Lower bound of the range (Hue, Saturation, Value)
#upper_bound = np.array([200, 255, 255])  # Upper bound of the range (Hue, Saturation, Value)

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
#fgbg = cv2.createBackgroundSubtractorKNN(detectShadows=False)




# Capture the video feed (or use an image)
cap = cv2.VideoCapture(0) #laptop camera


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
    
    combinedMask = cv2.bitwise_and(mask,fgmask)  #oombine the two masks
    #_, combinedMask = cv2.threshold(combinedMask, 127, 255, cv2.THRESH_BINARY)
    result = cv2.bitwise_and(frame,frame,mask=combinedMask) #apply combined mask to frame


    # Assuming 'combined_mask' is the binary mask image
    #check if can be changed to combinedMASk at foosball table
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
    #cv2.imshow("Foreground Mask",result2)
    #cv2.imshow("Final Mask",result)
    #cv2.imshow("Combined Mask",combinedMask)
    cv2.imshow("Output Frame",output_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
