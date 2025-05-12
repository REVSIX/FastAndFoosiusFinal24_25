// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy

// //Set up Serialization
// ArduinoController coms;

// // Constants for the number of motors and servos
// static const int numMotors = 4;
// static const int numServos = 4;

// // Arrays to store the positions of motors and servos
// float motorDesired[numMotors] = {0.5,0.5,0.5,0.5};
// float servoDesired[numServos] = {0.0,0.0,0.0,0.0};

// // Arrays to simulate current positions of motors and servos
// float motorCurrent[numMotors] = {0.0,0.0,0.0,0.0};
// float servoCurrent[numServos] = {0.0,0.0,0.0,0.0};


// Servo servo1, servo2, servo3, servo4; // Declare servo objects
// //float servoFlags[4] = {1.0, 1.0, 1.0, 1.0}; // Array to hold flags for each servo (0.0 for false, 1.0 for true)
// unsigned long previousMillis[4] = {0, 0, 0, 0}; // Stores the last time each servo was updated
// long interval = 100; // Interval at which to move servo (milliseconds)
// int currentStep[4] = {0, 0, 0, 0}; // To track the sequence of movements for each servo


// //servo 1
// int servop4 = 40;  //servo 4 output pin

// //servo 2
// int servop3 = 42;

// //servo 3
// int servop2 = 44;

// //servo 4
// int servop1 = 46;

// // Motor 4 pin definitions
// const int stepPin1 = 2;
// const int dirPin1 = 3;
// const int limitSwitchLow1 = A6;
// const int limitSwitchHigh1 = A7;

// // Motor 3 pin definitions
// const int stepPin2 = 4;
// const int dirPin2 = 5;
// const int limitSwitchLow2 = A4;
// const int limitSwitchHigh2 = A5;

// // Motor 2 pin definitions
// const int stepPin3 = 6;
// const int dirPin3 = 7;
// const int limitSwitchLow3 = A2;
// const int limitSwitchHigh3 = A3;

// // Motor 1 pin definitions
// const int stepPin4 = 8;
// const int dirPin4 = 9;
// const int limitSwitchLow4 = A0;
// const int limitSwitchHigh4 = A1;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed

// int angle1 = 0;
// int angle2 = 180;

// void setServoPosition(int servoIndex, int angle) {
//   switch (servoIndex) {
//     case 0:
//       servo1.write(int(48-(angle*4/5))); // 3/5 to accomodate for gear ratio
//       break;
//     case 1:
//       servo2.write(int(angle+60));
//       break;
//     case 2:
//       servo3.write(int(48-(angle*2.1/5))); // 3/5 to accomodate for gear ratio
//       break;
//     case 3:
//       servo4.write(int(angle+30));
//       break;
//   }
// }


// void homeServo(int servoIndex, int angle) {
//   for (int pos = 0; pos <= angle; pos += 1) { // Sweep from 0 to home degrees in 1 degree steps
//     setServoPosition(servoIndex, pos);
//     delay(15);
//   }
// }

// void moveServo(int servoIndex) {
//   for (int pos = angle1; pos <= angle2; pos += 5) { // Sweep from angle1 to angle2 degrees
//     setServoPosition(servoIndex, pos);
//     delay(15);
//   }
//   for (int pos = angle2; pos >= angle1; pos -= 5) { // Sweep from angle2 back to angle1 degrees
//     setServoPosition(servoIndex, pos);
//     delay(15);
//   }
// }



// int pos = 0;

// void setup() {
//   coms.setup();
//   // Set default servo positions before attaching
 

//   // Now attach servos
//   servo1.attach(servop1);
//   servo2.attach(servop2);
//   servo3.attach(servop3);
//   servo4.attach(servop4);
//     delay(50);
//   // Home each servo to a known position
 
//   homeServo(0, 0);
//   homeServo(1, 0);
//   homeServo(2, 0);
//   homeServo(3, 0);

//     delay(2000);

//   setServoPosition(0,-9);
//   setServoPosition(1,-9);
//   setServoPosition(2,-9);
//   setServoPosition(3,-9);

//     delay(3000);

//  // setServoPosition(0,0);

//   pinMode(limitSwitchLow1, INPUT_PULLUP);
//   pinMode(limitSwitchHigh1, INPUT_PULLUP);
//   pinMode(limitSwitchLow2, INPUT_PULLUP);
//   pinMode(limitSwitchHigh2, INPUT_PULLUP);
//   pinMode(limitSwitchLow3, INPUT_PULLUP);
//   pinMode(limitSwitchHigh3, INPUT_PULLUP);
//   pinMode(limitSwitchLow4, INPUT_PULLUP);
//   pinMode(limitSwitchHigh4, INPUT_PULLUP);
  


//   //Serial.begin(115200); // Initialize serial communication at 115200 baud, test

// }

// int algorithm = 1; // Declare and initialize the variable

// void loop() {
//   // The loop function can include logic to control each motor based on commands
//   // received from the Serial Monitor or another input method.

//   if (Serial.available() > 0) {

//     coms.loop(motorCurrent, servoCurrent);

//     servoCurrent[0] = servoCurrent[0] + coms.servoPositions[0];
//     servoCurrent[1] = servoCurrent[1] + coms.servoPositions[1];
//     servoCurrent[2] = servoCurrent[2] + coms.servoPositions[2];
//     servoCurrent[3] = servoCurrent[3] + coms.servoPositions[3];

//   }



//   unsigned long currentMillis = millis();

//   for (int i = 0; i < 4; i++) {
//     if (servoCurrent[i] != 0.0 && currentMillis - previousMillis[i] >= interval) {
//       previousMillis[i] = currentMillis; // Update last move time for this servo
      
    

//         // Determine angles based on the selected algorithm
//         if (algorithm == 1) { //Aggressive Kick
//         angle1 = 80; // Initial vertical position
//         angle2 = 140; // Slightly back
//         } else if (algorithm == 2) { //backward kicking
//         angle1 = 155; // Move backward
//         angle2 = 10; // Slightly forward
//         } else { //Standard algorithm
//         angle1 = 90; // Default position
//         angle2 = 135; // Default back position
//         }

//       moveServo(i);
//       currentStep[i]++;
//     }
//   }

// }
