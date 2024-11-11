from picamera2 import Picamera2
import cv2
import numpy as np

# Initialize the Picamera2 object
picam2 = Picamera2()

# Configure the camera for video capture
picam2.configure(picam2.create_video_configuration())

# Start the camera
picam2.start()


cap = cv2.VideoCapture(0)  # Force the V4L2 backend

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
