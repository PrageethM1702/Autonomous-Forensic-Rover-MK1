import cv2
import numpy as np
from ultralytics import YOLO
from scipy.linalg import block_diag

"""
Load YOLO model
The YOLO (You Only Look Once) model is used for object detection.
It predicts bounding boxes and class probabilities directly from an image in one evaluation.
'yolov10n.pt' is the pre-trained weights file for the model.
This model processes images or video streams for real-time detection.
"""
model = YOLO('yolov10n.pt')

"""
Define matrices for Kalman Filter
Kalman Filter is used for object tracking by estimating the state (position and velocity).
The filter works in two steps: prediction and update, refining the detected position over time.
'dt' represents the time interval between updates.
"""
dt = 1.0  # Time step (1 frame)

"""
State Transition Matrix (F)
This matrix models the system dynamics, relating the previous state to the current state.
Includes position and velocity updates for both x and y directions.
The diagonal '1's represent position propagation, and 'dt' handles velocity integration.
"""
F = np.array([
    [1, 0, dt, 0],
    [0, 1, 0, dt],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

"""
Measurement Matrix (H)
Maps the state space to the measurement space.
It ensures that the Kalman filter considers only the position components (x and y).
"""
H = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0]
])

"""
Measurement noise covariance matrix (R)
Represents uncertainty in the measurements (sensor noise).
The values on the diagonal specify noise in x and y measurements.
"""
R = np.array([
    [5, 0],
    [0, 5]
])

"""
Process noise covariance matrix (Q)
Accounts for model inaccuracies or unpredictable dynamics in the system.
'q' represents the uncertainty factor for position and velocity predictions.
"""
q = 0.1
Q = block_diag(q, q, q, q)

"""
Initial state (x0): [x, y, x_velocity, y_velocity]
Represents the starting values for position and velocity in x and y directions.
Initially, these values are set to zero, assuming no movement or position known.
"""
x = np.array([0, 0, 0, 0]).reshape(-1, 1)

"""
Initial covariance matrix (P)
Captures the initial uncertainty in the state estimation.
High values (500) indicate significant uncertainty in initial position and velocity.
"""
P = np.eye(4) * 500

"""
Colors and Fonts
Constants used for overlay and text properties in the output visualization.
"""
PERSON_COLOR = (0, 0, 255)  # Red color for the person overlay.
TEXT_COLOR = (255, 0, 0)    # Blue color for label text.
FONT = cv2.FONT_HERSHEY_SIMPLEX  # Specifies font type for labels.
FONT_SCALE = 0.5  # Font size for text.
FONT_THICKNESS = 1  # Thickness of the text in pixels.

"""
Define 50 filters for specific classes
Only objects belonging to these 50 predefined categories will be processed.
The class names correspond to the labels the YOLO model can detect.
"""
filter_classes = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich"
]

"""
Kalman Filter predict function
This function predicts the next state based on the current state and system dynamics.
It applies the state transition matrix (F) and adds process noise (Q) to update uncertainty.
"""
def kalman_predict(F, x, P, Q):
    x = F @ x  # State prediction using dynamics.
    P = F @ P @ F.T + Q  # The covariance matrix with process noise.
    return x, P

"""
Kalman Filter update function
This function refines the prediction using the actual measurement (from object detection).
It calculates the Kalman Gain and corrects the state and covariance accordingly.
"""
def kalman_update(x, P, Z, H, R):
    y = Z - H @ x  # Measurement residual (difference between predicted and actual measurement).
    S = H @ P @ H.T + R  # Residual covariance, considering measurement noise.
    K = P @ H.T @ np.linalg.inv(S)  # Kalman Gain, balancing prediction and measurement.
    x = x + K @ y  # Updated state estimate after correction.
    P = (np.eye(len(P)) - K @ H) @ P  # Updated uncertainty after correction.
    return x, P

"""
Function to detect and label all objects
This function runs the YOLO detection and visualizes the detected objects with overlays and labels.
"""
def detect_and_label():""" webcam based test"""
    results = model.predict(source=0, stream=True)

    for result in results:
        frame = result.orig_img  # Extract the original image frame from the detection result.
        frame = cv2.flip(frame, 1)  # Horizontally flips the frame for a more intuitive view.

        for box in result.boxes:
            coords = box.xyxy[0]  # Extracts the bounding box coordinates.
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            confidence = box.conf[0]  # Confidence score for the detected object.
            class_id = int(box.cls[0])  # Class ID for the detected object.
            label = model.names[class_id]  # Retrieves the class name based on the ID.

            # Filters detections by confidence threshold and predefined classes.
            confidence_threshold = 0.5  # Minimum confidence required to consider the detection.
            if confidence < confidence_threshold or label not in filter_classes:
                continue

            # Measurement matrix Z for Kalman Filter, based on the bounding box center.
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            Z = np.array([[center_x], [center_y]])

            # Kalman Filter for tracking: predict and update steps.
            global x, P
            x, P = kalman_predict(F, x, P, Q)
            x, P = kalman_update(x, P, Z, H, R)

            # Highlight detected person with a semi-transparent overlay.
            if label == "person":
                highlight_person(frame, x1, y1, x2, y2)

            # Draw the label above the detected object.
            draw_label(frame, x1, y1, label, confidence)

        cv2.imshow("Object Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

"""
Function to draw label with confidence
Add class name and confidence above the detected object in the frame.
"""
def draw_label(frame, x1, y1, label, confidence):
    text = f"{label} ({confidence:.2f})"  # Format label with class name and confidence score.
    cv2.putText(frame, text, (x1, y1 - 10), FONT, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS)

"""
Function to highlight person
Adds a semi-transparent red overlay for the detected person bounding box.
"""
def highlight_person(frame, x1, y1, x2, y2):
    overlay = frame.copy()  # Creates a copy of the frame for overlay blending.
    cv2.rectangle(overlay, (x1, y1), (x2, y2), PERSON_COLOR, -1)  # Draws a filled rectangle.
    alpha = 0.4  # Controls transparency (0: fully transparent, 1: fully opaque).
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)  # Blends the overlay with the frame.`

"""
Run detection and labeling
Executes the object detection pipeline, capturing frames and applying overlays.
"""
try:
    detect_and_label()
except Exception as e:
    print(f"Error: {e}")
