// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy
// #include "StepperControl.h"
// //Set up Serialization
// ArduinoController coms;

// const float EPS = .005;

// // OLD
// // // Define the two player positions (could be normalized positions or pixel-based)
// // const float player1Position = 0.6; // Position of player 1 (0% of the rod) //.8
// // const float player2Position = 0.4; // Position of player 2 (100% of the rod) //.1
// // const int pauseTime = 50; // Time to pause at each position in milliseconds

// // //CURRENT BEST
// // // Define the two player positions (could be normalized positions or pixel-based)
// // const float player1Position = 0.6; // Position of player 1 (0% of the rod) //.8
// // const float player2Position = 0.35; // Position of player 2 (100% of the rod) //.1
// // const int pauseTime = 50; // Time to pause at each position in milliseconds

// //NEW TEST
// // Define the two player positions (could be normalized positions or pixel-based)
// const float player1Position = 0.6; // Position of player 1 (0% of the rod) //.8
// const float player2Position = 0.4; // Position of player 2 (100% of the rod) //.1
// const int pauseTime = 50; // Time to pause at each position in milliseconds



// // Motor 2 pin definitions
// const int stepPin3 = 6;
// const int dirPin3 = 7;
// const int limitSwitchLow3 = A2;
// const int limitSwitchHigh3 = A3;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed

// // Create an instance of the StepperControl class
// StepperControl stepper2(stepPin3, dirPin3, stepsPerRevolution);


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

// void setup() {
//     // Initialize the stepper motor
//     coms.setup();
//     Serial.begin(115200);

//     pinMode(limitSwitchLow3, INPUT_PULLUP);
//     pinMode(limitSwitchHigh3, INPUT_PULLUP);

//     findLimits(stepper2, limitSwitchLow3, limitSwitchHigh3);

//     // stepper2.setLowLim(0);  // Assume the low limit is 0
//     // stepper2.setHighLim(1000);  // Assume the high limit is 1000 (number of steps on the rod)
//     // stepper2.setIdle();

//     stepper2.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
//     while (fabs(stepper2.getCurrentPosNorm() - player1Position) > EPS){
//         stepper2.update();  // Continuously update the motor position
//     }

//     delay(8000);
// }

// int numCycles = 200; // Number of times to go back and forth

// void loop() {
//     // Move to player 1's position

//     for (int i = 0; i < numCycles; i++) {
//         stepper2.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
//         while (fabs(stepper2.getCurrentPosNorm() - player1Position) > EPS){
//             stepper2.update();  // Continuously update the motor position
//         }
        
//         // Pause at player 1's position
//         delay(pauseTime);

//         // Move to player 2's position
//         stepper2.moveTo(player2Position, 1000);  // Move to player 2 position at a desired speed
//         while (fabs(stepper2.getCurrentPosNorm() - player2Position) > EPS) {
//             stepper2.update();  // Continuously update the motor position
//         }
        
//         // Pause at player 2's position
//         delay(pauseTime);

//         //Serial.println(i);

// }

//   // Halt here forever
//   while (true) {
//     // Optionally do nothing, or put the Arduino to sleep
//   }


// }
