import cv2
from picamera2 import Picamera2, Preview


picam= Picamera2()

config = picam.create_preview_configuration()
picam.configure(config)
picam.start()


cap = cv2.VideoCapture(1)  # Force the V4L2 backend

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
