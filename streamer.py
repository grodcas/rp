import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Force the V4L2 backend

if not cap.isOpened():
    print("Error: Camera not accessible.")
else:
    print("Camera is successfully opened.")
    
# Capture frame
ret, frame = cap.read()
if not ret:
    print("Failed to grab frame")
else:
    print("Frame captured successfully")

cap.release()
