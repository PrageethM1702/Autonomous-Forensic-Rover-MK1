# Autonomous-Forensic-Rover MK1
AI-powered autonomous rover for forensic investigations with injury classification, harmful gas detection and human navigation capabilities.

## Project Overview
The rover is designed to assist in forensic investigations by autonomously detecting humans, identifying injuries and detecting harmful gases in crime scenes.
### Key Features 
1. Human detection and navigation using CMOS 3MP Camera and YOLO-based deep learning.
2. Injury classification with custom .keras models.
3. High-quality injury photography using Raspberry Pi V2 Camera.
4. Harmful gas detection using MQ gas sensor series.
5. ESP32-controlled autonomous navigation with DC gear motors, servo motors, and motor drivers.


## AI Models
### Human Detection
1. Model: YOLOv10
2. Camera: CMOS 3MP
Purpose: Navigate the rover towards humans autonomously.
### Injury Classification
1. Model: Custom Deep Learning model built with .keras
2. Training Dataset: Medical injury dataset
3. Camera: Raspberry Pi V2
Purpose: Classify injuries as {}.

## Gas Detection System
### Gas Sensor Thresholds
This repository contains information about various gas sensors and their threshold values for detection.


## Autonomous Navigation & Injury Photography System

### Autonomous Navigation

| Component  | Details |
|------------|---------|
| **Controller** | ESP32 |
| **Motors** | DC Gear Motors + Servo Steering |
| **Algorithm** | A* Pathfinding + YOLO Obstacle Avoidance |

### Injury Photography System

| Camera          | Purpose              | Image Quality |
|----------------|----------------------|--------------|
| **CMOS 3MP**  | Human Detection       | 640×480      |
| **Raspberry Pi V2** | Injury Photography | 1080p        |

## Communication

| Component         | Protocol  |
|------------------|-----------|
| **Rover to Base** | WebSocket |
| **Gas Sensors**   | I2C       |
| **Cameras**       | HTTP Stream |

The **Autonomous Navigation & Injury Photography System** is a smart robotic platform designed for navigation and real-time injury detection. It utilizes an **ESP32** controller with **DC gear motors and servo steering**, guided by **A star pathfinding and YOLO-based obstacle avoidance** for autonomous movement. The injury photography system employs **CMOS 3MP and Raspberry Pi V2 cameras** to detect humans and capture high-quality injury images. Communication is handled via **WebSocket for rover-to-base transmission, I2C for gas sensors, and HTTP streaming for cameras**, ensuring efficient data transfer and remote monitoring. 
