import cv2
import time

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Test with 1920x1080 resolution
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

start_time = time.time()
frame_count = 0

while True:
    ret, frame = camera.read()
    if not ret:
        break

    frame_count += 1
    if frame_count >= 100:  # Measure time for 100 frames
        elapsed_time = time.time() - start_time
        print(f"1080p: {frame_count / elapsed_time:.2f} FPS")
        break

# Test with 1280x720 resolution
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

start_time = time.time()
frame_count = 0

while True:
    ret, frame = camera.read()
    if not ret:
        break

    frame_count += 1
    if frame_count >= 100:  # Measure time for 100 frames
        elapsed_time = time.time() - start_time
        print(f"720p: {frame_count / elapsed_time:.2f} FPS")
        break

camera.release()
