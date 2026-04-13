# MockingBird

## A gesture-controlled robotic hand for real-time motion tracking and replication

MockingBird is a wirelessly controlled robotic hand that mirrors human hand gestures using computer vision instead of wearable hardware. By combining MediaPipe hand tracking, OpenCV, Python sockets, and Raspberry Pi servo control, the system captures live finger movements from a camera feed and replicates them on a 3D-printed robotic hand with high precision.

Built as a UC Irvine EECS capstone project, MockingBird explores how natural hand movement can be translated into robotic motion for applications in remote interaction, industrial automation, assistive robotics, and future haptic systems.

Link to [Official Report](https://github.com/isaac-rico/MockingBird/blob/d4f6ce5df77a0793adb5e8362699f0c6baffa0fd/MockingBird%20Documentation.pdf) with images

---

## Project Features

- Real-time hand gesture tracking with MediaPipe
- Wireless communication using TCP sockets
- Servo-controlled 3D-printed robotic hand
- Raspberry Pi + PCA9685 based servo driver control
- Accurate finger angle replication
- Grip and pose testing support
- Expandable architecture for:
    - Haptic feedback
    - Pressure sensing
    - Wrist articulation
    - Industrial automation workflows


---

## Tech Stack
#### Software
- Python
- OpenCV
- MediaPipe
- NumPy
- Socket Programming (TCP / RFC 9293)
- Adafruit ServoKit

#### Hardware
- Raspberry Pi 5
- PCA9685 Servo Driver
- 25KG 300° Servos
- 3D Printed Hand Assembly
- 12V Battery
- Buck Converter
- Custom PCB Prototype

---

## How It Works
1. A camera captures the user’s hand movements
2. MediaPipe extracts hand landmarks in real time
3. Finger joint angles are calculated using NumPy + math
4. The angle data is sent wirelessly over TCP sockets
5. Raspberry Pi receives the data and maps it to servo positions
6. The robotic hand mirrors the gesture with ~0.5s delay

--- 

## Results

MockingBird successfully:
- Replicated open, closed, horns, and grip poses
- Demonstrated live hand tracking
- Achieved reliable wireless gesture mirroring
- Maintained stable grip control
- Reached sub-second response latency

The final prototype proved especially effective for pose replication and object gripping tasks.

--- 
## Security Considerations

Current system limitations include:

- No device authentication
- Any device on the same network can connect
- Limited failsafe controls
- Potential risks from incorrect gesture interpretation

Future versions should include:

- User authentication
- Emergency servo shutdown
- Safer disconnect behavior
- Misread gesture protection

---


## Future Improvements
- Haptic feedback system
- Full wrist articulation
- Authentication layer
- Lower latency networking
- Improved thumb articulation
- Stronger PCB power regulation
- Safer industrial deployment controls

---

## Authors
Isaac Rico
Neel Ramesh
Joey Balardeta
Matthew Conrad

**University of California, Irvine** 
EECS Capstone Project 2025