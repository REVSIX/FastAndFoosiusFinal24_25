// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy
// #include "Arduino.h"

// // Constants for motor control
// const int motorPin = 2;  // PWM pin to control motor speed
// const int dirPin = 3;    // Direction control pin for H-bridge

// void setup() {
//   // Initialize the motor control pins as outputs
//   pinMode(motorPin, OUTPUT);
//   pinMode(dirPin, OUTPUT);
  
//   // Start serial communication for debugging
//   Serial.begin(115200);
// }

// void loop() {
//   // Example: Move motor forward at different speeds

//   // Move forward
//   digitalWrite(dirPin, HIGH);  // Set direction (HIGH = forward)
  
//   // Ramp up speed from 0 to 255
//   for (int speed = 0; speed <= 127; speed += 5) {
//     analogWrite(motorPin, speed);  // Send PWM signal to motor
    
//     if (speed == 0) {
//       Serial.println("Motor is not moving.");
//     } else {
//       Serial.print("Motor speed: ");
//       Serial.println(speed);
//     }

//     delay(100);  // Wait for 100ms
//   }
  
//   delay(500);  // Run motor at full speed for 2 seconds
  
//   // Ramp down speed from 255 to 0
//   for (int speed = 127; speed >= 0; speed -= 5) {
//     analogWrite(motorPin, speed);  // Gradually slow down
    
//     if (speed == 0) {
//       Serial.println("Motor is not moving.");
//     } else {
//       Serial.print("Motor speed: ");
//       Serial.println(speed);
//     }
    
//     delay(100);  // Wait for 100ms
//   }
  
//   delay(500);  // Stop motor for 2 seconds
// }
