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

// const int trapAngle = -9;     // trap angle
// const int holdAngle = -75;
// const int shotAngle = 10;   // full 360 angle from trap angle
// const int receiveAngle = 9;
// const int fullAngle = 82;
// const int home = 0;
// const int rodIndex = 0; // change for which servo needed (only for servo 1 or 3 since they turn opposite directions)
// const int rodIndex2 = 1; //player receiving the ball // second servo used
// const int rodIndex3 = 0; //player receiving the ball // third servo used

// //Stepper Setup //change for which stepper being used

// // Motor 4 pin definitions
// const int stepPin4 = 2;
// const int dirPin4 = 3;
// const int limitSwitchLow4 = A6;
// const int limitSwitchHigh4 = A7;

// // Motor 3 pin definitions
// const int stepPin3 = 4;
// const int dirPin3 = 5;
// const int limitSwitchLow3 = A4;
// const int limitSwitchHigh3 = A5;

// // Motor 2 pin definitions
// const int stepPin2 = 6;
// const int dirPin2 = 7;
// const int limitSwitchLow2 = A2;
// const int limitSwitchHigh2 = A3;

// // Motor 1 pin definitions
// const int stepPin1 = 8;
// const int dirPin1 = 9;
// const int limitSwitchLow1 = A0;
// const int limitSwitchHigh1 = A1;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed
// const float EPS = 0.005;
// // Define the two player positions (could be normalized positions or pixel-based)
// const float player1Position = 0.4; // Position of player 1 (0% of the rod) //.8
// const float player2Position = 0.525; // Position of player 2 (100% of the rod) //.1
// const int pauseTime = 40; // Time to pause at each position in milliseconds
// int numCycles = 5; // Number of times to go back and forth

// // Initialize the stepper control objects for each motor
// StepperControl stepper1(stepPin1, dirPin1, stepsPerRevolution);
// StepperControl stepper2(stepPin2, dirPin2, stepsPerRevolution);
// StepperControl stepper4(stepPin4, dirPin4, stepsPerRevolution);
// StepperControl stepper3(stepPin3, dirPin3, stepsPerRevolution);


// void setServoPosition(int servoIndex, int angle) {
//     switch (servoIndex) {
//       case 0:
//         servo1.write(int(48-(angle*4/5))); // 3/5 to accomodate for gear ratio
//         break;
//       case 1:
//         servo2.write(int(angle+85));
//         break;
//       case 2:
//         servo3.write(int(48-(angle*2.1/5))); // 3/5 to accomodate for gear ratio
//         break;
//       case 3:
//         servo4.write(int(angle+21));
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

// //Algorithms

// //Ball Trap
// void performTrap() {
//     Serial.println("Trapping Ball");

//     setServoPosition(rodIndex,home);

//     delay(50);

//     setServoPosition(rodIndex,trapAngle);
  
//     delay(300);
  
//     Serial.println("Ball Trapped");
//   }

// //Shoot
// void performShot() {
//     Serial.println("Snake shot: spinning");
//     //only for servo 1
//     // Set players at angle to place ball trapped
//     setServoPosition(rodIndex,holdAngle);
//     delay(5000);  // Let it spin
  
//     // Spin 360 fast
//     setServoPosition(rodIndex,shotAngle);
//     delay(300);
  
//     Serial.println("Shot done");
//   }

// //Snake 
// void performSnake() {
//     findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);
//     findLimits(stepper1, limitSwitchLow1, limitSwitchHigh1);
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

// //Pass then snake (passing from rod 2 to rod 1 then snake at rod 1)
// void performPass2Snake() {
//   findLimits(stepper1, limitSwitchLow1, limitSwitchHigh1);
//   findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);

//   delay(500);
//   Serial.println("Passing");
//   // only for servo 1
//   //Set rods to line up the two passing players
//   stepper1.moveTo(.5, 1000);  // Move to player 1 position at a desired speed
//   while (fabs(stepper1.getCurrentPosNorm() - .5) > EPS) {
//       stepper1.update();  // Continuously update the motor position
//       delay(5);
//       //Serial.println(stepper1.getCurrentPosNorm());
//   }

//   delay(pauseTime);

//  stepper2.moveTo(0.5, 1000);
//    while (fabs(stepper2.getCurrentPosNorm() - 0.5) > EPS){
//       stepper2.update();  // Continuously update the motor position
//   }

//     delay(pauseTime);

//   // Set players at angle to place ball trapped
//   setServoPosition(rodIndex,trapAngle);
  
//   delay(8000);  // Give time to place ball under player
//   setServoPosition(rodIndex2,holdAngle);
//   delay(100);

//   // Set players at angle to place ball trapped
//   setServoPosition(rodIndex,receiveAngle);
  
//   Serial.println("Line Pass done");

  
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
//   setServoPosition(rodIndex2,shotAngle);
//   delay(300);

//   Serial.println("Pass to snake shot done");
// }

// // Line pass from rod 4 to rod 2
// void performLinePass() {
//   findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);
//   findLimits(stepper4, limitSwitchLow4, limitSwitchHigh4);
//   findLimits(stepper3, limitSwitchLow3, limitSwitchHigh3);
//   delay(500);
//   Serial.println("Passing");
//   // only for servo 1
//   //Set rods to line up the two passing players
//   stepper3.moveTo(0.5, 1000);
//   while (fabs(stepper3.getCurrentPosNorm() - 0.5) > EPS){
//      stepper3.update();  // Continuously update the motor position
//  }
//   stepper4.moveTo(0.5, 1000);
//    while (fabs(stepper4.getCurrentPosNorm() - 0.5) > EPS){
//       stepper4.update();  // Continuously update the motor position
//   }

//   delay(pauseTime);

//  stepper2.moveTo(0.5, 1000);
//    while (fabs(stepper2.getCurrentPosNorm() - 0.5) > EPS){
//       stepper2.update();  // Continuously update the motor position
//   }

//     delay(pauseTime);

//   // Set players at angle to place ball trapped
//   setServoPosition(rodIndex,trapAngle);
  
//   delay(8000);  // Give time to place ball under player
//   setServoPosition(rodIndex2,receiveAngle);
//   delay(25);
//   setServoPosition(rodIndex,receiveAngle);
//   delay(25);


//   Serial.println("Line Pass done");
// }

// // Pass from rod 2 to rod 1
// void performLinePass2() {
//   findLimits(stepper1, limitSwitchLow1, limitSwitchHigh1);
//   findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);
//   delay(500);
//   Serial.println("Passing");
//   // only for servo 1
//   //Set rods to line up the two passing players
//   stepper1.moveTo(.5, 1000);  // Move to player 1 position at a desired speed
//   while (fabs(stepper1.getCurrentPosNorm() - .5) > EPS) {
//       stepper1.update();  // Continuously update the motor position
//       delay(5);
//       //Serial.println(stepper1.getCurrentPosNorm());
//   }

//   delay(pauseTime);

//  stepper2.moveTo(0.5, 1000);
//    while (fabs(stepper2.getCurrentPosNorm() - 0.5) > EPS){
//       stepper2.update();  // Continuously update the motor position
//   }

//     delay(pauseTime);

//   // Set players at angle to place ball trapped
//   setServoPosition(rodIndex,trapAngle);
  
//   delay(8000);  // Give time to place ball under player
//   setServoPosition(rodIndex2,receiveAngle);
//   delay(25);
//   setServoPosition(rodIndex,receiveAngle);
//   delay(25);


//   Serial.println("Line Pass done");
// }


// //Passes from rod 4 to rod 2 to rod 1 then snake at rod 1
// void performPass2Pass2Snake() {
//     findLimits(stepper1, limitSwitchLow1, limitSwitchHigh1);
//     findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);
//     findLimits(stepper4, limitSwitchLow4, limitSwitchHigh4);
//     findLimits(stepper3, limitSwitchLow3, limitSwitchHigh3);
//     delay(500);
//     Serial.println("Passing");
//     delay(500);
//     // only for servo 1
//     //Set rods to line up the two passing players
//     stepper3.moveTo(0.5, 1000);
//     while (fabs(stepper3.getCurrentPosNorm() - 0.5) > EPS){
//        stepper3.update();  // Continuously update the motor position
//    }
//     stepper4.moveTo(0.5, 1000);
//      while (fabs(stepper4.getCurrentPosNorm() - 0.5) > EPS){
//         stepper4.update();  // Continuously update the motor position
//     }
  
//     delay(pauseTime);
  
//    stepper2.moveTo(0.5, 1000);
//      while (fabs(stepper2.getCurrentPosNorm() - 0.5) > EPS){
//         stepper2.update();  // Continuously update the motor position
//     }
  
//       delay(pauseTime);
  
//     // Set players at angle to place ball trapped
//     setServoPosition(rodIndex,trapAngle);
    
//     delay(8000);  // Give time to place ball under player
//     setServoPosition(rodIndex2,receiveAngle);
//     delay(75);
//     setServoPosition(rodIndex,receiveAngle);
//     delay(25);
//     // only for servo 1
//     //Set rods to line up the two passing players
//     stepper1.moveTo(.5, 1000);  // Move to player 1 position at a desired speed
//     while (fabs(stepper1.getCurrentPosNorm() - .5) > EPS) {
//         stepper1.update();  // Continuously update the motor position
//         delay(5);
//         //Serial.println(stepper1.getCurrentPosNorm());
//     }
  
//     delay(pauseTime);
  
//     delay(8000);  // Give time to place ball under player
//      // Set third player at angle to place ball trapped
//     setServoPosition(rodIndex3,holdAngle);
//     delay(1000);
//     setServoPosition(rodIndex2,fullAngle);
//     delay(100);
    
//     Serial.println("Line Pass done");
  
    
//     delay(8000);  // Give time to place ball under player
  
//     //move rod back and forth small distance quickly (to find open spot)
//     for (int i = 0; i < numCycles; i++) {
//         // Move to player 1 position
//         stepper1.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
//         while (fabs(stepper1.getCurrentPosNorm() - player1Position) > EPS) {
//             stepper1.update();  // Continuously update the motor position
//         }
    
//         // Pause at player 1's position
//         delay(pauseTime);
    
//         // Move to player 2 position
//         stepper1.moveTo(player2Position, 1000);  // Move to player 2 position at a desired speed
//         while (fabs(stepper1.getCurrentPosNorm() - player2Position) > EPS) {
//             stepper1.update();  // Continuously update the motor position
//         }
    
//         // Pause at player 2's position
//         delay(pauseTime);
//     }
//     delay(25);
  
//     // Spin 360 fast
//     setServoPosition(rodIndex3,shotAngle);
//     delay(300);
  
//     Serial.println("Pass to pass to snake shot done");
//   }
  

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

//   setServoPosition(0,0);
//   setServoPosition(1,0);
//   setServoPosition(2,0);
//   setServoPosition(3,0);
// }

// void loop() {
//   if (Serial.available()) {
//     String command = Serial.readStringUntil('\n');
//     if (command == "pass2snake") {
//       performPass2Snake();
//     }
//     else if  (command == "trap") {
//       performTrap();
//     }
//     else if (command == "shoot") {
//       performShot();
//     }
//     else if (command == "snake") {
//       performSnake();
//     }
//     else if (command == "pass") {
//       performLinePass();
//      }
//    else if (command == "pass2") {
//       performLinePass2();
//     }
//     else if (command == "pass2pass2snake") {
//       performPass2Pass2Snake();
//     }
//   }
// }
