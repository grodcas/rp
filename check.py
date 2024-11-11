import cv2
from flask import Flask, Response
from picamera2 import Picamera2
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

# Initialize the Flask app
app = Flask(__name__)

def generate_frames():
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()

        if not ret:
            print("Error: Failed to grab frame.")
            break

        print("Frame captured successfully.")

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Failed to encode frame.")
            break

        print("Frame encoded successfully.")

        frame = buffer.tobytes()

        # Yield the frame as part of the MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video')
def video():
    print("Video route accessed.")
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the app
if __name__ == '__main__':
    print("Starting the Flask web server...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
