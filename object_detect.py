from flask import Flask, Response, render_template
import cv2
from ultralytics import YOLO

app = Flask(__name__)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # Use 'yolov8s.pt' or others for better accuracy if resources allow

# Initialize the video capture
cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide a video file path

def generate_frames():
    """Generate frames from the webcam with YOLOv8 detection."""
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Perform YOLO detection
        results = model(frame)
        annotated_frame = results[0].plot()  # Annotate the frame with detection results

        # Encode the frame in JPEG format
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame in a streaming format for Flask
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Render the main webpage."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Return the video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
