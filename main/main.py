import os
import threading
import cv2
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify, Response
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from ultralytics import YOLO
from PIL import Image
import socket

app = Flask(__name__)

model_path = r"C:\BME\END PROJECT 2\body_det\kaggle\working\test_model_3.keras"
model = load_model(model_path)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

HOST = '192.168.69.204'
PORT = 8081

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def predict_image(img_path):
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    class_names = {0: 'Bruises', 1: 'Burns', 2: 'Cuts'}
    predicted_class_name = class_names.get(predicted_class, 'Unknown')
    return predicted_class_name, predicted_class

def send_command(command):
    try:
        client_socket.sendall(command.encode() + b'\n')
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        img = Image.open(filename)
        img.thumbnail((400, 400))
        img.save(filename)
        predicted_class_name, predicted_class = predict_image(filename)
        return jsonify({
            'prediction': predicted_class_name,
            'image_url': filename
        })

    return jsonify({"error": "Invalid file format"})

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    command = data.get('command')
    if command == "FORWARD":
        send_command("BACKWARD")
    elif command == "BACKWARD":
        send_command("FORWARD")
    elif command == "STOP":
        send_command("STOP")
    else:
        return jsonify({"status": "error", "message": "Invalid command"})
    return jsonify({"status": "success", "message": f"Command '{command}' sent"})

def generate_frames():
    yolo_model = YOLO('yolov10n.pt')
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = yolo_model(frame)
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id == 0:
                    coords = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, coords)
                    confidence = box.conf[0]
                    label = "person"
                    if confidence > 0.5:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"{label}: {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_socket_server():
    global client_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on {HOST}:{PORT}")
    print("Waiting for ESP32 to connect...")
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)

if __name__ == "__main__":
    socket_thread = threading.Thread(target=run_socket_server)
    socket_thread.daemon = True
    socket_thread.start()
    run_flask()