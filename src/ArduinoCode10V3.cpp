#include <Servo.h>
#include "StepperControl.h"
#include "ArduinoController.h"
#include <ArduinoJson.h>
#include <Arduino.h>
#include <string.h>  // For memcpy

ArduinoController coms;

static const int numMotors = 4;
static const int numServos = 4;

float motorDesired[numMotors] = {0.5, 0.5, 0.5, 0.5};
float servoDesired[numServos] = {0.0, 0.0, 0.0, 0.0};

float motorCurrent[numMotors] = {0.0, 0.0, 0.0, 0.0};
float servoCurrent[numServos] = {0.0, 0.0, 0.0, 0.0};

Servo servo1, servo2, servo3, servo4;
unsigned long previousMillis[4] = {0, 0, 0, 0};
long interval = 100;
int currentStep[4] = {0, 0, 0, 0};

int servop4 = 40;
int servop3 = 42;
int servop2 = 44;
int servop1 = 46;

const int stepPin1 = 2;
const int dirPin1 = 3;
const int limitSwitchLow1 = A6;
const int limitSwitchHigh1 = A7;

const int stepPin2 = 4;
const int dirPin2 = 5;
const int limitSwitchLow2 = A4;
const int limitSwitchHigh2 = A5;

const int stepPin3 = 6;
const int dirPin3 = 7;
const int limitSwitchLow3 = A2;
const int limitSwitchHigh3 = A3;

const int stepPin4 = 8;
const int dirPin4 = 9;
const int limitSwitchLow4 = A0;
const int limitSwitchHigh4 = A1;

const int stepsPerRevolution = 200;

StepperControl stepper4(stepPin1, dirPin1, stepsPerRevolution);
StepperControl stepper3(stepPin2, dirPin2, stepsPerRevolution);
StepperControl stepper2(stepPin3, dirPin3, stepsPerRevolution);
StepperControl stepper1(stepPin4, dirPin4, stepsPerRevolution);

void findLimits(StepperControl &stepper, int lowSwitch, int highSwitch) {
  while (digitalRead(lowSwitch) == HIGH) {
    stepper.runAtSpeed(0.5, -1);
    stepper.update();
    delay(5);
  }
  stepper.stop();
  stepper.setLowLim(stepper.getCurrentPosition());

  while (digitalRead(highSwitch) == HIGH) {
    stepper.runAtSpeed(0.5, 1);
    stepper.update();
    delay(5);
  }
  stepper.stop();
  stepper.setHighLim(stepper.getCurrentPosition());
}

void setServoPosition(int servoIndex, int angle) {
  switch (servoIndex) {
    case 0:
      servo1.write(int(48 - (angle * 4 / 5)));
      break;
    case 1:
      servo2.write(int(angle + 72));
      break;
    case 2:
      servo3.write(int(48 - (angle * 2.1 / 5)));
      break;
    case 3:
      servo4.write(int(angle + 30));
      break;
  }
}

void homeServo(int servoIndex, int angle) {
  for (int pos = 0; pos <= angle; pos += 1) {
    setServoPosition(servoIndex, pos);
    delay(15);
  }
}

void performTrap(int servoIndex) {
  Serial.println("Trapping Ball");
  setServoPosition(servoIndex, 0);
  delay(50);
  setServoPosition(servoIndex, 9);
  delay(300);
  Serial.println("Ball Trapped");
  setServoPosition(servoIndex, 0);
}

void setup() {
  coms.setup();

  servo1.attach(servop1);
  servo2.attach(servop2);
  servo3.attach(servop3);
  servo4.attach(servop4);

  delay(1000);
  homeServo(0, 0);
  homeServo(1, 0);
  homeServo(2, 0);
  homeServo(3, 0);

  pinMode(limitSwitchLow1, INPUT_PULLUP);
  pinMode(limitSwitchHigh1, INPUT_PULLUP);
  pinMode(limitSwitchLow2, INPUT_PULLUP);
  pinMode(limitSwitchHigh2, INPUT_PULLUP);
  pinMode(limitSwitchLow3, INPUT_PULLUP);
  pinMode(limitSwitchHigh3, INPUT_PULLUP);
  pinMode(limitSwitchLow4, INPUT_PULLUP);
  pinMode(limitSwitchHigh4, INPUT_PULLUP);

  findLimits(stepper1, limitSwitchLow4, limitSwitchHigh4);
  findLimits(stepper2, limitSwitchLow3, limitSwitchHigh3);
  findLimits(stepper3, limitSwitchLow2, limitSwitchHigh2);
  findLimits(stepper4, limitSwitchLow1, limitSwitchHigh1);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("trap")) {
      int index = command.charAt(4) - '0';
      if (index >= 0 && index < 4) {
        performTrap(index);
      }
    } else {
      motorCurrent[0] = stepper1.getCurrentPosNorm();
      motorCurrent[1] = stepper2.getCurrentPosNorm();
      motorCurrent[2] = stepper3.getCurrentPosNorm();
      motorCurrent[3] = stepper4.getCurrentPosNorm();

      coms.loop(motorCurrent, servoCurrent);

      servoCurrent[0] += coms.servoPositions[0];
      servoCurrent[1] += coms.servoPositions[1];
      servoCurrent[2] += coms.servoPositions[2];
      servoCurrent[3] += coms.servoPositions[3];
    }
  }

  stepper1.moveTo(coms.motorPositions[0], .3);
  stepper2.moveTo(coms.motorPositions[1], .3);
  stepper3.moveTo(coms.motorPositions[2], .3);
  stepper4.moveTo(coms.motorPositions[3], .3);
  stepper1.update();
  stepper2.update();
  stepper3.update();
  stepper4.update();

  unsigned long currentMillis = millis();
  for (int i = 0; i < 4; i++) {
    if (servoCurrent[i] != 0.0 && currentMillis - previousMillis[i] >= interval) {
      previousMillis[i] = currentMillis;
      int angle1 = -10, angle2 = 10;

      switch (currentStep[i]) {
        case 0:
          setServoPosition(i, angle1);
          interval = 215;
          break;
        case 1:
          setServoPosition(i, angle2);
          interval = 115;
          break;
        case 2:
          setServoPosition(i, angle1);
          currentStep[i] = -1;
          servoCurrent[i] = 0.0;
          break;
      }
      currentStep[i]++;
    } else if (servoCurrent[i] == 0.0) {
      setServoPosition(i, 20);
    }
  }
}