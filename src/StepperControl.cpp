#include "StepperControl.h"

StepperControl::StepperControl(int stepPin, int dirPin, int stepsPerRevolution) {
    pinMode(stepPin, OUTPUT);
    pinMode(dirPin, OUTPUT);
    _stepPin = stepPin;
    _dirPin = dirPin;
    _stepsPerRevolution = stepsPerRevolution;
    _currentPosition = 0;
    _targetPosition = 0;
    _lastStepTime = 0;
    _highLim = 0;
    _lowLim = 0;
    _state = IDLE; // Motor starts in an idle state
    _runDirection = 1; // Default direction
    _initialStepDelay = 2000; // Initial step delay for smooth start
    // _minStepDelay = 200; // Minimum step delay at full speed
    // _maxStepDelay = 2000; // Maximum step delay for slowest speed or start/stop
    // _acceleration = 100; // Number of steps to reach full speed


    //// TICTAC
    // _minStepDelay = 200; // Minimum step delay at full speed
    // _maxStepDelay = 1000; // Maximum step delay for slowest speed or start/stop
    // _acceleration = 300; // Number of steps to reach full speed

    // // // TICTAC CURRENT BEST
    // _minStepDelay = 250; // Minimum step delay at full speed
    // _maxStepDelay = 2000; // Maximum step delay for slowest speed or start/stop
    // _acceleration = 120; // Number of steps to reach full speed

    // // TICTAC NEW
    _minStepDelay = 250; // Minimum step delay at full speed
    _maxStepDelay = 2000; // Maximum step delay for slowest speed or start/stop
    _acceleration = 100; // Number of steps to reach full speed


    // // //SNAKE SHIFT OVER (trapped)
    // _minStepDelay = 1900; // Minimum step delay at full speed
    // _maxStepDelay = 2000; // Maximum step delay for slowest speed or start/stop
    // _acceleration = 1000; // Number of steps to reach full speed


}

void StepperControl::setLowLim(int lim){
    _lowLim = lim;
}

void StepperControl::setHighLim(int lim){
    _highLim = lim;
}

void StepperControl::moveTo(float position, float speed) {
    _targetPosition = (int)(_lowLim + position * (_highLim - _lowLim));
    _stepDelay = _maxStepDelay;
    _speedIncrement = (_maxStepDelay - _minStepDelay) / _acceleration;
    _state = MOVING;
}

void StepperControl::runAtSpeed(float speed, int direction) {
    _stepDelay = _maxStepDelay;
    _speedIncrement = (_maxStepDelay - _minStepDelay) / _acceleration;
    _runDirection = direction >= 0 ? 1 : -1;
    _state = RUNNING;
}

void StepperControl::stop() {
    _state = IDLE;
}

void StepperControl::setIdle() {
    _state = IDLE;
}

void StepperControl::update() {
    switch (_state) {
        case MOVING:
            stepToTarget();
            break;
        case RUNNING:
            runContinuous();
            break;
        case IDLE:
            // Do nothing
            break;
    }
}

void StepperControl::stepMotor(int step) {
    digitalWrite(_dirPin, step > 0 ? HIGH : LOW);
    digitalWrite(_stepPin, HIGH);
    delayMicroseconds(100); // Short pulse to trigger one step
    digitalWrite(_stepPin, LOW);
}

void StepperControl::runContinuous() {
    unsigned long currentTime = micros();
    if (currentTime - _lastStepTime >= _stepDelay) {
        if (_stepDelay > _minStepDelay) _stepDelay -= _speedIncrement;
        stepMotor(_runDirection);
        _currentPosition += _runDirection;
        _lastStepTime = currentTime;
    }
}

void StepperControl::stepToTarget() {
    unsigned long currentTime = micros();
    if (currentTime - _lastStepTime >= _stepDelay) {
        int stepsToGo = abs(_targetPosition - _currentPosition);
        if (stepsToGo < _acceleration) {
            _stepDelay += _speedIncrement; // Decelerate
        } else if (_stepDelay > _minStepDelay) {
            _stepDelay -= _speedIncrement; // Accelerate
        }

        if (_currentPosition < _targetPosition) {
            stepMotor(1);
            _currentPosition++;
        } else if (_currentPosition > _targetPosition) {
            stepMotor(-1);
            _currentPosition--;
        }
        _lastStepTime = currentTime;
        if (stepsToGo == 0) _state = IDLE; // Stop when target is reached
    }
}

int StepperControl::getCurrentPosition() {
    return _currentPosition;
}

float StepperControl::getCurrentPosNorm() {
    if (_highLim == _lowLim) {  // To prevent division by zero
        return .5;  // or consider returning an error or default value
    }
    return float(_currentPosition - _lowLim) / float(_highLim - _lowLim);
}
