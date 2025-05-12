// #include <Servo.h>
// #include "Arduino.h"  //include because it a .cpp file instead of a .ino file

// Servo myServo;  // create a servo object to control a servo
// int currentPosition = 0; // initial position of servo

// void setup() {
//   Serial.begin(115200);  // start serial communication
//   myServo.attach(10);   // attaches the servo on pin 9 to the servo object
// }

// void loop() {
//   if (Serial.available() > 0) {
//     int targetPosition = Serial.parseInt();  // read target position from serial
//     targetPosition = constrain(targetPosition, 0, 180);  // constrain to valid range for a servo
//     myServo.write(targetPosition);  // move servo to the target position
//     delay(1000);  // wait for servo to reach position

//     currentPosition = targetPosition;
//     Serial.println(currentPosition);  // send current position back to Python
//   }
// }


// //-----------------------------------------------------------------------

// // #include <Servo.h>
// // #include "Arduino.h"  //include because it a .cpp file instead of a .ino file
// // Servo myServo;  // Create a Servo object

// // void setup() {
// //     Serial.begin(115200);  // start serial communication
// //     myServo.attach(10);  // Attach servo to pin 9
// // }

// // void loop() {
// //     myServo.write(90);  // Move to 90 degrees
// //     Serial.println("90");
// //     delay(2000);  // Wait 2 seconds
// //     myServo.write(45);  // Move to 45 degrees
// //     delay(2000);  // Wait 2 seconds
// // }
