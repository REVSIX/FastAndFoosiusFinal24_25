// #include <Servo.h>
// #include <ArduinoJson.h>
// #include <string.h>  // For memcpy
// #include "ArduinoController.h"


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

// ArduinoController coms;

// const int home = 0;
// const int trapAngle = -9;     // Trap Angle
// const int rodIndex = 0; // change for which servo needed (only for servo 1)
// const int holdAngle = -75;
// const int shotAngle = 10;   // little less than 360 back to homing spot


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
//     if (command == "shoot") {
//       performShot();
//     }
//   }
// }


