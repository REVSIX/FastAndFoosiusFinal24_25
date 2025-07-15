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
//   switch (servoIndex) {
//     case 0:
//       servo1.write(int(43-(angle*4.3/5))); // 3/5 to accomodate for gear ratio
//       break;
//     case 1:
//       servo2.write(int(angle+16));
//       break;
//     case 2:
//       servo3.write(int(37-(angle*2.2/5))); // 3/5 to accomodate for gear ratio
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



// void setup() {
//   coms.setup();

//   servo1.attach(servop1); // Attach each servo to a different pin
//   servo2.attach(servop2);
//   servo3.attach(servop3);
//   servo4.attach(servop4);

//   delay(1000);

//   homeServo(0, 0);
//   homeServo(1, 0);
//   homeServo(2, 0);
//   homeServo(3, 0); 

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

// void loop() {
//     // If there's serial data available
//     if (Serial.available() > 0) {
  
//       // Update current positions from stepper motors
//       motorCurrent[0] = stepper1.getCurrentPosNorm();
//       motorCurrent[1] = stepper2.getCurrentPosNorm();
//       motorCurrent[2] = stepper3.getCurrentPosNorm();
//       motorCurrent[3] = stepper4.getCurrentPosNorm();
  
//       // Get desired positions from Python
//       coms.loop(motorCurrent, servoCurrent);
  
//       // Determine if new kick has been requested for each servo
//       for (int i = 0; i < 4; i++) {
//         int desiredKick = int(coms.servoPositions[i]);  // Read command as integer (0–3)
//         // change max type num if adding more kicks
//         if (desiredKick > 0 && desiredKick <= 3 && servoCurrent[i] == 0.0) {
//           servoCurrent[i] = desiredKick;  // Store desired kick type
//           currentStep[i] = 0;             // Reset step sequence
//         }
//       }
//     }
  
//     // Move steppers to desired positions
//     stepper1.moveTo(coms.motorPositions[0], 0.3);
//     stepper2.moveTo(coms.motorPositions[1], 0.3);
//     stepper3.moveTo(coms.motorPositions[2], 0.3);
//     stepper4.moveTo(coms.motorPositions[3], 0.3);
  
//     // Update stepper states
//     stepper1.update();
//     stepper2.update();
//     stepper3.update();
//     stepper4.update();
  
//     // Time-based servo control for kicking
//     unsigned long currentMillis = millis();
  
//     for (int i = 0; i < 4; i++) {
//       if (servoCurrent[i] != 0.0 && currentMillis - previousMillis[i] >= interval) {
//         previousMillis[i] = currentMillis; // Update last move time for this servo
        
//         // Determine angles based on desired kick type
//         int angle1 = 0, angle2 = 0;
//         switch (int(servoCurrent[i])) {
//           case 1:  // Standard kick
//             angle1 = -10;
//             angle2 = 10;
//             break;
//           case 2:  // Powerful forward kick
//             angle1 = -60;
//             angle2 = 10;
//             break;
//           case 3:  // Backward kick
//             angle1 = -10;
//             angle2 = 20;
//             break;
//           default:
//             angle1 = 0;
//             angle2 = 0;
//             break;
//         }
  
//         // Perform the sequence of kick motions
//         switch (currentStep[i]) {
//           case 0:
//             setServoPosition(i, angle1); // Kick start
//             interval = 215;
//             break;
//           case 1:
//             setServoPosition(i, angle2); // Follow-through
//             interval = 115;
//             break;
//           case 2:
//             setServoPosition(i, 0); // Return to neutral
//             currentStep[i] = -1;    // Stop sequence
//             servoCurrent[i] = 0.0;  // Reset servo kick state
//             break;
//         }
//         currentStep[i]++;
//       }
//     }
//   }
  