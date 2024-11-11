from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Initialize the Picamera2 object
picam2 = Picamera2()

# Check if the camera is accessible
try:
    # Configure the camera for video capture
    picam2.configure(picam2.create_video_configuration())
    picam2.start()
    print("Camera initialized successfully.")
except Exception as e:
    print(f"Error initializing camera: {e}")
    exit(1)

# OpenCV window to display the video feed
cv2.namedWindow("Video Feed", cv2.WINDOW_NORMAL)

# Capture and display video frames
while True:
    try:
        # Capture a frame from picamera2
        frame = picam2.capture_array()

        if frame is None:
            print("Failed to grab frame.")
            continue  # Skip if no frame is captured
        
        # Display the frame
        cv2.imshow("Video Feed", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error during frame capture: {e}")
        break

# Release the camera and close the window
picam2.stop()
cv2.destroyAllWindows()
