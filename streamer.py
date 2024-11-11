from flask import Flask, Response
from picamera2 import Picamera2
import time
import cv2
import numpy as np

app = Flask(__name__)

# Initialize picamera2
picam2 = Picamera2()

# Configure the camera for video capture (set a higher resolution)
picam2.configure(picam2.create_video_configuration(
    main={"size": (1920, 1080), "format": "YUV420"}))  # Set resolution and format
picam2.start()

def generate():
    while True:
        # Capture a frame from picamera2
        frame = picam2.capture_array()
        
        if frame is not None:
            # Convert from YUV (or BGR if OpenCV) to RGB to fix color issues
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_YV12)  # Convert YUV to RGB

            # Compress the frame into JPEG format
            ret, jpeg = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 90])  # Set JPEG quality to 90
            if ret:
                # Yield the frame in MJPEG format for streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        time.sleep(0.1)  # Adjust the frame rate if needed

@app.route('/')
def index():
    return "MJPEG Streaming is running!"

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
