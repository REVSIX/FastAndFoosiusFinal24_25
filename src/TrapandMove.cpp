// #include <Servo.h>
// #include "StepperControl.h"
// #include "ArduinoController.h"
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy
// #include "StepperControl.h"
// //Set up Serialization
// ArduinoController coms;

// const float EPS = .005;


// Servo servo2; // Declare servo objects


// // Define the two player positions (could be normalized positions or pixel-based)
// const float player1Position = .4; // Position of player 1 (0% of the rod) //.8
// const float player2Position = .525; // Position of player 2 (100% of the rod) //.1
// const int pauseTime = 100; // Time to pause at each position in milliseconds

// // Motor 2 pin definitions
// const int stepPin3 = 6;
// const int dirPin3 = 7;
// const int limitSwitchLow3 = A2;
// const int limitSwitchHigh3 = A3;

// const int stepsPerRevolution = 200; // Common for all motors, adjust if needed

// //servo 3
// int servop2 = 44;



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
//     servo2.write(0);
//     coms.setup();

//     servo2.attach(servop2);
//     servo2.write(25);
//     delay(1000);
//     pinMode(limitSwitchLow3, INPUT_PULLUP);
//     pinMode(limitSwitchHigh3, INPUT_PULLUP);

//     findLimits(stepper2, limitSwitchLow3, limitSwitchHigh3);
    

//     stepper2.moveTo(player1Position, 1000);
//     while (fabs(stepper2.getCurrentPosNorm() - player1Position) > EPS){
//         stepper2.update();  // Continuously update the motor position
//     }
//     delay(10000);


//     // stepper2.setLowLim(0);  // Assume the low limit is 0
//     // stepper2.setHighLim(1000);  // Assume the high limit is 1000 (number of steps on the rod)
//     // stepper2.setIdle();
// }


// int numCycles = 5; // Number of times to go back and forth

// void loop() {
//     // Move to player 1's position
//     for (int i = 0; i < numCycles; i++) {
//         // Move to player 1 position
//         stepper2.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
//         while (fabs(stepper2.getCurrentPosNorm() - player1Position) > EPS) {
//             stepper2.update();  // Continuously update the motor position
//         }
    
//         // Pause at player 1's position
//         delay(pauseTime);
    
//         // Move to player 2 position
//         stepper2.moveTo(player2Position, 1000);  // Move to player 2 position at a desired speed
//         while (fabs(stepper2.getCurrentPosNorm() - player2Position) > EPS) {
//             stepper2.update();  // Continuously update the motor position
//         }
    
//         // Pause at player 2's position
//         delay(pauseTime);
//     }

//     delay(pauseTime);
//     servo2.write(140);

//     delay(pauseTime);
//     //servo2.write(27);




// }







// // stepper2.moveTo(player1Position, 1000);  // Move to player 1 position at a desired speed
// // while (fabs(stepper2.getCurrentPosNorm() - player1Position) > EPS){
// //     stepper2.update();  // Continuously update the motor position
// // }

// // // Pause at player 1's position
// // delay(pauseTime);

// // // Move to player 2's position
// // stepper2.moveTo(player2Position, 1000);  // Move to player 2 position at a desired speed
// // while (fabs(stepper2.getCurrentPosNorm() - player2Position) > EPS) {
// //     stepper2.update();  // Continuously update the motor position
// // }

// // // Pause at player 2's position
// // delay(pauseTime);