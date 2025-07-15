# 🕹️ Autonomous Foosball Table

Welcome to the **Autonomous Foosball Table** project! This repository contains all Python and Arduino code used to develop and simulate a robotic foosball defense system using stepper motors, servos, and a webcam. The table tracks and reacts to a ball in real-time using computer vision and PID/Kalman-based control logic.

Built on top of the `FastAndFossiusFinal24_25` project, this iteration combines mechanical capabilities with offensive logic and coordinated system movement.

---

## 📁 Repository Structure

### `python/`
This folder contains multiple iterations of the foosball table logic. Each Python file represents a different approach or technique tested over time.

**Current stable version:**
python/mainKalmanFixRodCenterScale.py

---

### `python/foosScope/`
This is the virtual simulator environment, called **FoosScope**.

⚠️ It is still under heavy development and not yet fully stable.

- `mainKalmanFixRodCenterScale.py` runs the real system with hardware.
- FoosScope is a sandboxed virtual version designed for testing and visualizing strategies.

---

### `src/` (Arduino Code)
This folder contains Arduino code iterations for controlling motors, servos, and other hardware.

**Current stable version:**
src/ArduinoCode10.cpp

💡 To isolate and test a specific version, comment out unused scripts or only include the one you're testing in `platformio.ini`.

---

## 🔧 Hardware Summary

This system uses:
- 🌀 Stepper Motors for rod linear motion
- 🔧 Arduino Servos for player rotation/kicking
- 🎥 Webcam for tracking the ball via computer vision

---

## ⚙️ Setup Guide

### 📍 PlatformIO (for Arduino code)
1. Install [VS Code](https://code.visualstudio.com/)
2. Install the **PlatformIO** extension from the Extensions tab
3. Open the project folder
4. Use the PlatformIO toolbar to:
   - Select the correct board (e.g. Arduino Uno, Mega)
   - Build (✓)
   - Upload (→) to your Arduino board

💡 To test a new `.cpp` version, comment out all others and leave just one active in `src/`.

---

### 🐍 Python Setup (for ball tracking + simulation)
1. Make sure you have **Python 3.8+** installed
2. Install the required libraries:

pip install numpy opencv-python matplotlib\

3. Run the main control logic:

python python/mainKalmanFixRodCenterScale.py


Other scripts are for development or experimentation.

---

## 🛠️ Notes

- Ensure the webcam is positioned above the foosball table with minimal distortion
- You may need to tune PID values and motor travel limits based on your table setup

---

## 🚧 Ongoing Development

- **Foosscope** is an early-stage simulator for testing strategies virtually
- We're working on:
  - Kalman filtering for more accurate ball prediction
  - Coordinated rod movement
  - Smarter offense/defense switching and behavior

---

Feel free to open issues, contribute code, or fork the project for your own robotics experiments!
