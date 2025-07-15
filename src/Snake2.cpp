// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy
// #include "StepperControl.h"
// //Set up Serialization
// ArduinoController coms;

// //Servo Setup
// Servo servo1, servo2, servo3, servo4; // Declare servo objects
// //servo 1
// int servop4 = 40;  //servo 4 output pin

// //servo 2
// int servop3 = 42;

// //servo 3
// int servop2 = 44;

// //servo 4
// int servop1 = 46;


// const int home = 0;
// const int trapAngle = -9;     // Trap Angle
// const int rodIndex = 2; // change for which servo needed (only for servo 1)
// const int holdAngle = -75;
// const int shotAngle = 10;   // little less than 360 back to homing spot


// //Stepper Setup //change for which stepper being used
// // // Motor 1 pin definitions
// // const int stepPin = 8;
// // const int dirPin = 9;
// // const int limitSwitchLow = A0;
// // const int limitSwitchHigh = A1;

// // Motor 3 pin definitions
// const int stepPin = 4;
// const int dirPin = 5;
// const int limitSwitchLow = A4;
// const int limitSwitchHigh = A5;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed
// const float EPS = 0.005;
// // Define the two player positions (could be normalized positions or pixel-based)
// const float player1Position = 0.4; // Position of player 1 (0% of the rod) //.8
// const float player2Position = 0.525; // Position of player 2 (100% of the rod) //.1
// const int pauseTime = 40; // Time to pause at each position in milliseconds
// int numCycles = 5; // Number of times to go back and forth

// // Initialize the stepper control objects for each motor
// StepperControl stepper1(stepPin, dirPin, stepsPerRevolution);

// void setServoPosition(int servoIndex, int angle) {
//     switch (servoIndex) {
//       case 0:
//         servo1.write(int(45-(angle*4.1/5))); // 3/5 to accomodate for gear ratio
//         break;
//       case 1:
//         servo2.write(int(angle+66));
//         break;
//       case 2:
//         servo3.write(int(31-(angle*2.2/5))); // 3/5 to accomodate for gear ratio
//         break;
//       case 3:
//         servo4.write(int(angle+29));
//         break;
//     }
//   }

// void findLimits(StepperControl &stepper, int lowSwitch, int highSwitch) {
//     //Serial.println("Finding low limit...");
//     while (digitalRead(lowSwitch) == HIGH) {
//       stepper.runAtSpeed(0.5, -1);
//       stepper.update();
//       delay(5); // Short delay to slow down the search
//     }
//     stepper.stop();
//     stepper.setLowLim(stepper.getCurrentPosition());
  
//     //Serial.println("Finding high limit...");
//     while (digitalRead(highSwitch) == HIGH) {
//       stepper.runAtSpeed(0.5, 1);
//       stepper.update();
//       delay(5); // Short delay to slow down the search
//     }
//     stepper.stop();
//     stepper.setHighLim(stepper.getCurrentPosition());
  
//     //Serial.println("Limits set.");
//   }



// //Function
// void performSnake() {
//   delay(500);
//   Serial.println("Snake shot: spinning");
//   // only for servo 1
//   //Set rod to middle position
//   stepper1.moveTo(0.5, 1000);
//    while (fabs(stepper1.getCurrentPosNorm() - 0.5) > EPS){
//       stepper1.update();  // Continuously update the motor position
//   }
 
//   delay(pauseTime);

//   // Set players at angle to place ball trapped
//   setServoPosition(rodIndex,holdAngle);
  
//   delay(8000);  // Give time to place ball under player

//   //move rod back and forth small distance quickly (to find open spot)
//   for (int i = 0; i < numCycles; i++) {
//       // Move to player 1 position
//       stepper1.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
//       while (fabs(stepper1.getCurrentPosNorm() - player1Position) > EPS) {
//           stepper1.update();  // Continuously update the motor position
//       }
  
//       // Pause at player 1's position
//       delay(pauseTime);
  
//       // Move to player 2 position
//       stepper1.moveTo(player2Position, 1000);  // Move to player 2 position at a desired speed
//       while (fabs(stepper1.getCurrentPosNorm() - player2Position) > EPS) {
//           stepper1.update();  // Continuously update the motor position
//       }
  
//       // Pause at player 2's position
//       delay(pauseTime);
//   }
//   delay(25);

//   // Spin 360 fast
//   setServoPosition(rodIndex,shotAngle);
//   delay(300);

//   Serial.println("Snake shot done");
// }

// void setup() {
//   coms.setup();
//   // Set default servo positions before attaching
//   findLimits(stepper1, limitSwitchLow, limitSwitchHigh);
//   // Now attach servos
//   servo1.attach(servop1);
//   servo2.attach(servop2);
//   servo3.attach(servop3);
//   servo4.attach(servop4);
//     delay(50);
//   // Home each servo to a known position

//   setServoPosition(0,0);
//   setServoPosition(1,0);
//   setServoPosition(2,0);
//   setServoPosition(3,0);
// }



// void loop() {
//   if (Serial.available()) {
//     String command = Serial.readStringUntil('\n');
//     if (command == "snake") {
//       performSnake();
//     }
//   }
// }


