import cv2
import numpy as np
import math

def calc_point(center, R, angle):
    return (int(center[0] + R * math.cos(angle)),
            int(center[1] - R * math.sin(angle)))

def main():
    img_size = 500
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    center = (img_size // 2, img_size // 2)
    R = img_size // 3
    
    KF = cv2.KalmanFilter(2, 1, 0)
    KF.transitionMatrix = np.array([[1, 1], [0, 1]], np.float32)
    KF.measurementMatrix = np.array([[1, 0]], np.float32)
    KF.processNoiseCov = np.array([[1e-5, 0], [0, 1e-5]], np.float32)
    KF.measurementNoiseCov = np.array([[1e-1]], np.float32)
    KF.errorCovPost = np.array([[1, 0], [0, 1]], np.float32)
    KF.statePost = np.random.randn(2, 1).astype(np.float32) * 0.1
    
    state = np.array([[0.0], [2 * np.pi / 6]], np.float32)
    
    while True:
        img[:] = (0, 0, 0)
        state[0, 0] += state[1, 0] + np.random.randn() * 1e-5
        
        state_pt = calc_point(center, R, state[0, 0])
        prediction = KF.predict()
        predict_pt = calc_point(center, R, prediction[0, 0])
        
        measurement = np.array([[state[0, 0] + np.random.randn() * 1e-1]], np.float32)
        meas_pt = calc_point(center, R, measurement[0, 0])
        
        KF.correct(measurement)
        improved_pt = calc_point(center, R, KF.statePost[0, 0])
        
        img = (img * 0.2).astype(np.uint8)
        cv2.drawMarker(img, meas_pt, (0, 0, 255), cv2.MARKER_SQUARE, 5, 2)
        cv2.drawMarker(img, predict_pt, (0, 255, 255), cv2.MARKER_SQUARE, 5, 2)
        cv2.drawMarker(img, improved_pt, (0, 255, 0), cv2.MARKER_SQUARE, 5, 2)
        cv2.drawMarker(img, state_pt, (255, 255, 255), cv2.MARKER_STAR, 10, 1)
        cv2.line(img, state_pt, meas_pt, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.line(img, state_pt, predict_pt, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.line(img, state_pt, improved_pt, (0, 255, 0), 1, cv2.LINE_AA)
        
        cv2.imshow("Kalman", img)
        key = cv2.waitKey(1000)
        if key in [27, ord('q'), ord('Q')]:
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
