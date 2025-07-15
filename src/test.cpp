// #include <Servo.h>
// #include "StepperControl.h"


// // === Stepper motor pins ===
// // Motor 4
// const int stepPin1 = 2;
// const int dirPin1 = 3;
// const int limitSwitchLow1 = A6;
// const int limitSwitchHigh1 = A7;


// // Motor 3
// const int stepPin2 = 4;
// const int dirPin2 = 5;
// const int limitSwitchLow2 = A4;
// const int limitSwitchHigh2 = A5;


// // Motor 2
// const int stepPin3 = 6;
// const int dirPin3 = 7;
// const int limitSwitchLow3 = A2;
// const int limitSwitchHigh3 = A3;


// // Motor 1
// const int stepPin4 = 8;
// const int dirPin4 = 9;
// const int limitSwitchLow4 = A0;
// const int limitSwitchHigh4 = A1;


// // === Servos ===
// Servo servo1, servo2, servo3, servo4;
// const int servop1 = 46;
// const int servop2 = 44;
// const int servop3 = 42;
// const int servop4 = 40;


// // === Stepper setup ===
// const int stepsPerRevolution = 200;
// StepperControl stepper4(stepPin1, dirPin1, stepsPerRevolution);
// StepperControl stepper3(stepPin2, dirPin2, stepsPerRevolution);
// StepperControl stepper2(stepPin3, dirPin3, stepsPerRevolution);
// StepperControl stepper1(stepPin4, dirPin4, stepsPerRevolution);


// // === Helper: set servo position using main code’s mapping ===
// void setServoPosition(int servoIndex, int angle) {
//   switch (servoIndex) {
//     case 0:
//       servo1.write(int(48 - (angle * 4 / 5)));
//       break;
//     case 1:
//       servo2.write(int(angle + 72));
//       break;
//     case 2:
//       servo3.write(int(48 - (angle * 2.1 / 5)));
//       break;
//     case 3:
//       servo4.write(int(angle + 30));
//       break;
//   }
// }


// // === Helper: find stepper limits ===
// void findLimits(StepperControl &stepper, int lowSwitch, int highSwitch) {
//   while (digitalRead(lowSwitch) == HIGH) {
//     stepper.runAtSpeed(0.5, -1);
//     stepper.update();
//     delay(5);
//   }
//   stepper.stop();
//   stepper.setLowLim(stepper.getCurrentPosition());


//   while (digitalRead(highSwitch) == HIGH) {
//     stepper.runAtSpeed(0.5, 1);
//     stepper.update();
//     delay(5);
//   }
//   stepper.stop();
//   stepper.setHighLim(stepper.getCurrentPosition());
// }


// void setup() {
//   Serial.begin(115200);


//   // Attach servos
//   servo1.attach(servop1);
//   servo2.attach(servop2);
//   servo3.attach(servop3);
//   servo4.attach(servop4);


//   delay(1000);


//   // Set servo to neutral
//   setServoPosition(0, 0);
//   setServoPosition(1, 0);
//   setServoPosition(2, 0);
//   setServoPosition(3, 0);


//   // Set up limit switches
//   pinMode(limitSwitchLow1, INPUT_PULLUP);
//   pinMode(limitSwitchHigh1, INPUT_PULLUP);
//   pinMode(limitSwitchLow2, INPUT_PULLUP);
//   pinMode(limitSwitchHigh2, INPUT_PULLUP);
//   pinMode(limitSwitchLow3, INPUT_PULLUP);
//   pinMode(limitSwitchHigh3, INPUT_PULLUP);
//   pinMode(limitSwitchLow4, INPUT_PULLUP);
//   pinMode(limitSwitchHigh4, INPUT_PULLUP);


//   // Find limits
//   findLimits(stepper1, limitSwitchLow4, limitSwitchHigh4);
//   findLimits(stepper2, limitSwitchLow3, limitSwitchHigh3);
//   findLimits(stepper3, limitSwitchLow2, limitSwitchHigh2);
//   findLimits(stepper4, limitSwitchLow1, limitSwitchHigh1);
// }


// void loop() {
//   const int testSteps = 50;
//   const float testSpeed = 0.5;


//   // === Stepper forward ===
//   stepper1.moveTo(stepper1.getCurrentPosition() + testSteps, testSpeed); delay(500);
//   stepper2.moveTo(stepper2.getCurrentPosition() + testSteps, testSpeed); delay(500);
//   stepper3.moveTo(stepper3.getCurrentPosition() + testSteps, testSpeed); delay(500);
//   stepper4.moveTo(stepper4.getCurrentPosition() + testSteps, testSpeed); delay(500);


//   for (int i = 0; i < testSteps; i++) {
//     stepper1.update();
//     stepper2.update();
//     stepper3.update();
//     stepper4.update();
//     delay(10);
//   }


//   // === Stepper backward ===
//   stepper1.moveTo(stepper1.getCurrentPosition() - testSteps, testSpeed); delay(500);
//   stepper2.moveTo(stepper2.getCurrentPosition() - testSteps, testSpeed); delay(500);
//   stepper3.moveTo(stepper3.getCurrentPosition() - testSteps, testSpeed); delay(500);
//   stepper4.moveTo(stepper4.getCurrentPosition() - testSteps, testSpeed); delay(500);


//   for (int i = 0; i < testSteps; i++) {
//     stepper1.update();
//     stepper2.update();
//     stepper3.update();
//     stepper4.update();
//     delay(10);
//   }


//   // === Servo sweep ===
//   for (int angle = 0; angle <= 90; angle += 5) {
//     setServoPosition(0, angle); delay(500);
//     setServoPosition(1, angle); delay(500);
//     setServoPosition(2, angle); delay(500);
//     setServoPosition(3, angle); delay(500);
//   }
//   for (int angle = 90; angle >= 0; angle -= 5) {
//     setServoPosition(0, angle); delay(500);
//     setServoPosition(1, angle); delay(500);
//     setServoPosition(2, angle); delay(500);
//     setServoPosition(3, angle); delay(500);
//   }


//   delay(1000); // Rest between cycles
// }
