#include <AFMotor.h>

// Initialize stepper motors on M1, M2, M3, and M4 with 200 steps per revolution
AF_Stepper motor1(200, 1);  // M1 and M2
AF_Stepper motor2(200, 2);  // M3 and M4

// Motor state variables
bool motor1Running = false;
bool motor2Running = false;
int motor1Direction = 0;
int motor2Direction = 0;
int motorSpeed = 60; // Default speed

void setup() {
    Serial.begin(9600); // Start serial communication
    motor1.setSpeed(motorSpeed);
    motor2.setSpeed(motorSpeed);
}

void loop() {
    if (Serial.available()) {
        char command = Serial.read();

        if (command == 'S') {
            while (Serial.available() == 0);
            motorSpeed = Serial.parseInt();
            if (motorSpeed > 0) {
                motor1.setSpeed(motorSpeed);
                motor2.setSpeed(motorSpeed);
            }
        } else {
            switch (command) {
                case 'U':
                    motor1Direction = 1;  // Move Up (Forward)
                    motor1Running = true;
                    break;
                case 'D':
                    motor1Direction = -1; // Move Down (Backward)
                    motor1Running = true;
                    break;
                case 'L':
                    motor2Direction = -1; // Move Left (Backward)
                    motor2Running = true;
                    break;
                case 'R':
                    motor2Direction = 1;  // Move Right (Forward)
                    motor2Running = true;
                    break;
                case 'X':
                    motor1Running = false;
                    motor2Running = false;
                    motor1.release();
                    motor2.release();
                    break;
            }
        }
    }

    if (motor1Running) {
        if (motor1Direction == 1) {
            motor1.step(1, FORWARD, INTERLEAVE);
        } else if (motor1Direction == -1) {
            motor1.step(1, BACKWARD, INTERLEAVE);
        }
    }

    if (motor2Running) {
        if (motor2Direction == 1) {
            motor2.step(1, FORWARD, INTERLEAVE);
        } else if (motor2Direction == -1) {
            motor2.step(1, BACKWARD, INTERLEAVE);
        }
    }
}
