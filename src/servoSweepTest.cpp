// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy

// Servo myServo;
// int sweepCount = 0;
// const int maxSweeps = 5;

// void setup() {
//   myServo.attach(46); // Attach the servo to pin 9
// }

// void loop() {
//   if (sweepCount < maxSweeps) {
//     // Sweep from 0 to 180
//     for (int pos = 0; pos <= 60; pos += 5) {
//       myServo.write(pos);
//       delay(25); // Delay for smooth motion
//     }
//     // Sweep back from 180 to 0
//     for (int pos = 60; pos >= 0; pos -= 5) {
//       myServo.write(pos);
//       delay(25);
//     }
//     sweepCount++;
//   } else {
//     // Stop moving the servo after 20 sweeps
//     myServo.detach(); // Optional: detach to stop sending PWM
//     while (true); // Halt further execution
//   }
// }