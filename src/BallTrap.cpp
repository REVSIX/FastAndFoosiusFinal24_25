// #include <Servo.h>
// #include <ArduinoJson.h>
// #include "ArduinoController.h"
// #include <string.h>  // For memcpy

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
// const int trapAngle = 9;     // Trap Angle, change sign depending on direction
// const int rodIndex = 2; // change for which servo needed

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

// void performTrap() {
//     Serial.println("Trapping Ball");

//     setServoPosition(rodIndex,home);

//     delay(50);

//     setServoPosition(rodIndex,trapAngle);
  
//     delay(300);
  
//     Serial.println("Ball Trapped");
//   }

// void setup() {
//     coms.setup();
//     // Set default servo positions before attaching
   
//     // Now attach servos
//     servo1.attach(servop1);
//     servo2.attach(servop2);
//     servo3.attach(servop3);
//     servo4.attach(servop4);
//       delay(50);
//     // Home each servo to a known position
  
//     setServoPosition(0,0);
//     setServoPosition(1,0);
//     setServoPosition(2,0);
//     setServoPosition(3,0);
// }

// void loop() {
//   if (Serial.available()) {
//     String command = Serial.readStringUntil('\n');
//     if (command == "trap") {
//       performTrap();
//     }
//   }
// }


