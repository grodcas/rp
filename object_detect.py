import cv2
from ultralytics import YOLO

# Load a YOLOv8 model pre-trained on the COCO dataset
model = YOLO('yolov8n.pt')  # 'yolov8n.pt' is the nano version for fast inference

# Open webcam feed or use a video file
cap = cv2.VideoCapture(0)  # Replace 0 with a file path for video input

if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Run YOLO detection on the frame
    results = model(frame)

    # Visualize results
    annotated_frame = results[0].plot()  # Annotate frame with detection results

    # Show the annotated frame
    cv2.imshow('YOLOv8 Object Detection', annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
