import cv2

# Initialize the camera (0 is the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access the camera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show the frame in a window
        cv2.imshow('Camera', frame)

        # Exit if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
