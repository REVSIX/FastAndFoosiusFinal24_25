# import cv2


# def find_working_camera(max_ports=10):
#     print("Scanning for available camera ports...")
#     for index in range(max_ports):
#         cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
#         if cap.isOpened():
#             ret, frame = cap.read()
#             if ret:
#                 print(f"Camera found on port {index}")
#                 return cap  # Return the opened camera object
#         cap.release()
#     print("No working camera found.")
#     return None


# def main():
#     cap = find_working_camera()


#     if cap is None:
#         return


#     # Optional: Set resolution
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


#     print("Camera initialized. Press 'q' to exit.")


#     while True:
#         ret, frame = cap.read()


#         if not ret:
#             print("Failed to grab frame.")
#             break


#         cv2.imshow("Camera Preview", frame)


#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Quitting camera preview.")
#             break


#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()