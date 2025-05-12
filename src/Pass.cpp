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
// const int receiveAngle = 10;
// const int home = 0;
// const int rodIndex = 3; // change for which servo needed (only for servo 1 or 3 since they turn opposite directions)
// const int rodIndex2 = 1; //player receiving the ball

// //Stepper Setup //change for which stepper being used
// // Motor 4 pin definitions
// const int stepPin4 = 2;
// const int dirPin4 = 3;
// const int limitSwitchLow4 = A6;
// const int limitSwitchHigh4 = A7;

// // Motor 2 pin definitions
// const int stepPin2 = 6;
// const int dirPin2 = 7;
// const int limitSwitchLow2 = A2;
// const int limitSwitchHigh2 = A3;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed
// const float EPS = 0.005;
// // Define the two player positions (could be normalized positions or pixel-based)
// const float player1Position = 0.4; // Position of player 1 (0% of the rod) //.8
// const float player2Position = 0.525; // Position of player 2 (100% of the rod) //.1
// const int pauseTime = 40; // Time to pause at each position in milliseconds
// int numCycles = 5; // Number of times to go back and forth

// // Initialize the stepper control objects for each motor
// StepperControl stepper4(stepPin4, dirPin4, stepsPerRevolution);
// StepperControl stepper2(stepPin2, dirPin2, stepsPerRevolution);

// void setServoPosition(int servoIndex, int angle) {
//   switch (servoIndex) {
//     case 0:
//       servo1.write(int(45-(angle*4.1/5))); // 3/5 to accomodate for gear ratio
//       break;
//     case 1:
//       servo2.write(int(angle+63));
//       break;
//     case 2:
//       servo3.write(int(31-(angle*2.2/5))); // 3/5 to accomodate for gear ratio
//       break;
//     case 3:
//       servo4.write(int(angle+29));
//       break;
//   }
// }

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
// void performLinePass() {
 
//   delay(500);
//   Serial.println("Passing");
//   // only for servo 1
//   //Set rods to line up the two passing players
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

// void setup() {
//   coms.setup();
//   // Set default servo positions before attaching
//   findLimits(stepper4, limitSwitchLow4, limitSwitchHigh4);
//   findLimits(stepper2, limitSwitchLow2, limitSwitchHigh2);
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
//     if (command == "pass") {
//       performLinePass();
//     }
//   }
// }


