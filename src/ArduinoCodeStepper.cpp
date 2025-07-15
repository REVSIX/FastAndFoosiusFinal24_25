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
// int servop4 = 10;  //servo 4 output pin

// //servo 2
// int servop3 = 11;

// //servo 3
// int servop2 = 12;

// //servo 4
// int servop1 = 13;

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

// // Initialize the stepper control objects for each motor
// StepperControl stepper4(stepPin1, dirPin1, stepsPerRevolution);
// StepperControl stepper3(stepPin2, dirPin2, stepsPerRevolution);
// StepperControl stepper2(stepPin3, dirPin3, stepsPerRevolution);
// StepperControl stepper1(stepPin4, dirPin4, stepsPerRevolution);

// void findLimits(StepperControl &stepper, int lowSwitch, int highSwitch) {
//   //Serial.println("Finding low limit...");
//   while (digitalRead(lowSwitch) == HIGH) {
//     stepper.runAtSpeed(0.5, -1);
//     stepper.update();
//     delay(5); // Short delay to slow down the search
//   }
//   stepper.stop();
//   stepper.setLowLim(stepper.getCurrentPosition());

//   //Serial.println("Finding high limit...");
//   while (digitalRead(highSwitch) == HIGH) {
//     stepper.runAtSpeed(0.5, 1);
//     stepper.update();
//     delay(5); // Short delay to slow down the search
//   }
//   stepper.stop();
//   stepper.setHighLim(stepper.getCurrentPosition());

//   //Serial.println("Limits set.");
// }

// void setServoPosition(int servoIndex, int angle) {
//     switch (servoIndex) {
//       case 0:
//         servo1.write(angle);
//         break;
//       case 1:
//         servo2.write(angle);
//         break;
//       case 2:
//         servo3.write(angle);
//         break;
//       case 3:
//         servo4.write(angle);
//         break;
//     }
//   }
  

// void homeServo(int servoIndex, int angle) {
//   for (int pos = 0; pos <= angle; pos += 1) { // Sweep from 0 to home degrees in 1 degree steps
//     setServoPosition(servoIndex, pos);
//     delay(15);
//   }
// }



// void setup() {
//   coms.setup();

//   servo1.attach(servop1); // Attach each servo to a different pin
//   servo2.attach(servop2);
//   servo3.attach(servop3);
//   servo4.attach(servop4);

//   homeServo(0, 5);
//   homeServo(1, 24);
//   homeServo(2, 7);
//   homeServo(3, 15); 

//   pinMode(limitSwitchLow1, INPUT_PULLUP);
//   pinMode(limitSwitchHigh1, INPUT_PULLUP);
//   pinMode(limitSwitchLow2, INPUT_PULLUP);
//   pinMode(limitSwitchHigh2, INPUT_PULLUP);
//   pinMode(limitSwitchLow3, INPUT_PULLUP);
//   pinMode(limitSwitchHigh3, INPUT_PULLUP);
//   pinMode(limitSwitchLow4, INPUT_PULLUP);
//   pinMode(limitSwitchHigh4, INPUT_PULLUP);
  
//   findLimits(stepper1, limitSwitchLow4, limitSwitchHigh4);
//   findLimits(stepper2, limitSwitchLow3, limitSwitchHigh3);
//   findLimits(stepper3, limitSwitchLow2, limitSwitchHigh2);
//   findLimits(stepper4, limitSwitchLow1, limitSwitchHigh1);

//   //Serial.begin(115200); // Initialize serial communication at 115200 baud, test

// }

// int algorithm = 3; // Declare and initialize the variable

// void loop() {
//     static bool goingUp = true; // Direction flag
//     static float target = 0.0;  // Target normalized position
//     static unsigned long lastMoveTime = 0;
//     unsigned long now = millis();
  
//     // Only move every 10 ms (adjust as needed for smoother motion)
//     if (now - lastMoveTime >= 10) {
//       lastMoveTime = now;
  
//       // Get current position
//       float currentPos = stepper1.getCurrentPosNorm();
  
//       // Check if we've reached target
//       if (goingUp && currentPos >= 1.0) {
//         goingUp = false;
//       } else if (!goingUp && currentPos <= 0.0) {
//         goingUp = true;
//       }
  
//       // Set new target depending on direction
//       target = goingUp ? 1.0 : 0.0;
  
//       // Move to target at a slow speed
//       stepper1.moveTo(target, 0.3);
//     }
  
//     stepper1.update();
//   }
  





