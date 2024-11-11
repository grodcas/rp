import cv2
from flask import Flask, Response

# Initialize the Flask app
app = Flask(__name__)

# Initialize the camera (0 is the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Camera is not accessible.")
else:
    print("Camera is successfully opened.")

def generate_frames():
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

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