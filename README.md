🕹️ Autonomous Foosball Table
Welcome to the Autonomous Foosball Table project! This repository contains all Python and Arduino code used to develop and simulate a robotic foosball defense system using stepper motors, servos, and a webcam. The table tracks and reacts to a ball in real-time using computer vision and PID/Kalman-based control logic. Built on top of the [FastAndFossiusFinal24_25](https://github.com/MayaGharat/Fast-Foosius24_25)
project, this iteration intends to combine the mechanical capabilities of the project with offensive logic and coordinated system movement.

📁 Repository Structure
python/
This folder contains multiple iterations of the foosball table logic. Each Python file represents a different approach or technique tested over time.

The current stable version is:

bash
Copy
Edit
python/mainKalmanFixRodCenterScale.py
python/foosscope/
This is the virtual simulator environment, called Foosscope.

It is still under heavy development and not yet fully stable.

While mainKalmanFixRodCenterScale.py runs the real system with hardware, Foosscope is a sandboxed virtual version being designed for testing and visualizing strategies.

src/ (Arduino Code)
This folder contains Arduino code iterations, controlling the hardware interface (motors, servos, etc.).

Each .cpp file is a separate version or attempt.

The current stable version is:

css
Copy
Edit
src/ArduinoCode10.cpp
💡 To isolate and test a specific version, comment out unused scripts or only include the one you're testing in the platformio.ini.

🔧 Hardware Summary
This system uses:

Stepper Motors for rod linear motion

Arduino Servos for player rotation/kicking

Webcam for tracking the position and velocity of the ball via computer vision

⚙️ Setup Guide
📍 PlatformIO (for Arduino code)
Install VS Code if you haven't already.

Install the PlatformIO extension from the Extensions tab.

Open the project folder.

Use the PlatformIO toolbar to:

Select the correct board (Arduino Uno, Mega, etc.)

Build (✓)

Upload (→) to your Arduino board

To test a new .cpp version, comment out all others and leave just one active in src/.

🐍 Python Setup (for ball tracking + simulation)
Ensure you have Python 3.8+ installed.

Install the required libraries:

bash
Copy
Edit
pip install numpy opencv-python matplotlib
Run the main control logic:

bash
Copy
Edit
python python/mainKalmanFixRodCenterScale.py
(Other scripts are for development/experimental purposes.)

🛠️ Notes
Make sure the webcam is positioned over the foosball table with minimal distortion.

You may need to tune PID values and motor ranges based on your table’s physical configuration.

🚧 Ongoing Development
Foosscope is an exciting simulator project being built to test control logic without needing physical hardware.

We're actively exploring improvements to ball prediction (Kalman Filtering), rod coordination, and event-based strategy.

Feel free to open issues, contribute code, or fork the project for your own robotics experiments.
