from flask import Flask, Response
from picamera2 import Picamera2, Preview
import time
import cv2

app = Flask(__name__)

# Initialize Picamera2
picam2 = Picamera2()

# Configure the camera for video capture
picam2.configure(picam2.create_video_configuration())

# Adjust the focus if the camera supports it
# This will only work if your camera has adjustable focus.

picam2.start()

def generate():
    while True:
        # Capture a frame from Picamera2
        frame = picam2.capture_array()

        if frame is not None:
            # Convert the frame to JPEG format for MJPEG streaming
            ret, jpeg = cv2.imencode('.jpg', frame)
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
