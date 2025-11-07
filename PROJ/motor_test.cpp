// motor_test.cpp
// Simple motor test program for the two-wheeled following car
// Tests basic motor control without GUI or buttons

#include <iostream>
#include <chrono>
#include <thread>
#include <signal.h>
#include <wiringPi.h>

using namespace std;

// Motor pin configuration (same as your Python version)
struct MotorPins {
    int in1;
    int in2;
    int pwm;
    string name;
};

// Motor configurations
const MotorPins LEFT_MOTOR = {5, 6, 26, "Left"};
const MotorPins RIGHT_MOTOR = {20, 21, 16, "Right"};

// PWM settings
const int PWM_FREQUENCY = 50;  // Hz
const int FULL_SPEED = 99;     // 99% duty cycle
const int STOP_SPEED = 0;      // 0% duty cycle

// Global flag for graceful shutdown
volatile bool running = true;

void signalHandler(int signum) {
    cout << "\nReceived signal " << signum << ". Stopping motors..." << endl;
    running = false;
}

void stopAllMotors() {
    // Stop left motor
    digitalWrite(LEFT_MOTOR.in1, LOW);
    digitalWrite(LEFT_MOTOR.in2, LOW);
    pwmWrite(LEFT_MOTOR.pwm, STOP_SPEED);

    // Stop right motor
    digitalWrite(RIGHT_MOTOR.in1, LOW);
    digitalWrite(RIGHT_MOTOR.in2, LOW);
    pwmWrite(RIGHT_MOTOR.pwm, STOP_SPEED);

    cout << "All motors stopped." << endl;
}

void controlMotor(const MotorPins& motor, string direction, int speed) {
    if (direction == "CW") {
        // Clockwise
        digitalWrite(motor.in1, HIGH);
        digitalWrite(motor.in2, LOW);
        pwmWrite(motor.pwm, speed);
        cout << motor.name << " motor: Clockwise at " << speed << "% speed" << endl;
    }
    else if (direction == "CCW") {
        // Counter-clockwise
        digitalWrite(motor.in1, LOW);
        digitalWrite(motor.in2, HIGH);
        pwmWrite(motor.pwm, speed);
        cout << motor.name << " motor: Counter-clockwise at " << speed << "% speed" << endl;
    }
    else if (direction == "STOP") {
        // Stop
        digitalWrite(motor.in1, LOW);
        digitalWrite(motor.in2, LOW);
        pwmWrite(motor.pwm, STOP_SPEED);
        cout << motor.name << " motor: Stopped" << endl;
    }
}

void setupGPIO() {
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        cerr << "Failed to initialize wiringPi!" << endl;
        exit(1);
    }

    // Set up left motor pins
    pinMode(LEFT_MOTOR.in1, OUTPUT);
    pinMode(LEFT_MOTOR.in2, OUTPUT);
    pinMode(LEFT_MOTOR.pwm, PWM_OUTPUT);

    // Set up right motor pins
    pinMode(RIGHT_MOTOR.in1, OUTPUT);
    pinMode(RIGHT_MOTOR.in2, OUTPUT);
    pinMode(RIGHT_MOTOR.pwm, PWM_OUTPUT);

    // Set PWM frequency and range
    pwmSetMode(PWM_MODE_MS);
    pwmSetRange(100);  // 0-100% duty cycle
    pwmSetClock(PWM_FREQUENCY);

    // Initialize all pins to LOW
    digitalWrite(LEFT_MOTOR.in1, LOW);
    digitalWrite(LEFT_MOTOR.in2, LOW);
    digitalWrite(RIGHT_MOTOR.in1, LOW);
    digitalWrite(RIGHT_MOTOR.in2, LOW);
    pwmWrite(LEFT_MOTOR.pwm, STOP_SPEED);
    pwmWrite(RIGHT_MOTOR.pwm, STOP_SPEED);

    cout << "GPIO setup complete." << endl;
}

void testMotors() {
    cout << "\n=== Motor Test Sequence ===" << endl;

    // Test 1: Forward motion (both motors clockwise)
    cout << "\nTest 1: Moving forward..." << endl;
    controlMotor(LEFT_MOTOR, "CW", FULL_SPEED);
    controlMotor(RIGHT_MOTOR, "CW", FULL_SPEED);
    this_thread::sleep_for(chrono::seconds(3));

    // Stop
    stopAllMotors();
    this_thread::sleep_for(chrono::seconds(1));

    // Test 2: Backward motion (both motors counter-clockwise)
    cout << "\nTest 2: Moving backward..." << endl;
    controlMotor(LEFT_MOTOR, "CCW", FULL_SPEED);
    controlMotor(RIGHT_MOTOR, "CCW", FULL_SPEED);
    this_thread::sleep_for(chrono::seconds(3));

    // Stop
    stopAllMotors();
    this_thread::sleep_for(chrono::seconds(1));

    // Test 3: Turn left (left motor slower, right motor normal)
    cout << "\nTest 3: Turning left..." << endl;
    controlMotor(LEFT_MOTOR, "CW", FULL_SPEED / 2);
    controlMotor(RIGHT_MOTOR, "CW", FULL_SPEED);
    this_thread::sleep_for(chrono::seconds(3));

    // Stop
    stopAllMotors();
    this_thread::sleep_for(chrono::seconds(1));

    // Test 4: Turn right (left motor normal, right motor slower)
    cout << "\nTest 4: Turning right..." << endl;
    controlMotor(LEFT_MOTOR, "CW", FULL_SPEED);
    controlMotor(RIGHT_MOTOR, "CW", FULL_SPEED / 2);
    this_thread::sleep_for(chrono::seconds(3));

    // Stop
    stopAllMotors();
    this_thread::sleep_for(chrono::seconds(1));

    // Test 5: Spin in place (opposite directions)
    cout << "\nTest 5: Spinning in place..." << endl;
    controlMotor(LEFT_MOTOR, "CW", FULL_SPEED);
    controlMotor(RIGHT_MOTOR, "CCW", FULL_SPEED);
    this_thread::sleep_for(chrono::seconds(3));

    // Stop
    stopAllMotors();
    this_thread::sleep_for(chrono::seconds(1));

    // Test 6: Variable speed test
    cout << "\nTest 6: Variable speed test..." << endl;
    for (int speed = 25; speed <= 100; speed += 25) {
        cout << "Testing at " << speed << "% speed..." << endl;
        controlMotor(LEFT_MOTOR, "CW", speed);
        controlMotor(RIGHT_MOTOR, "CW", speed);
        this_thread::sleep_for(chrono::seconds(2));
        stopAllMotors();
        this_thread::sleep_for(chrono::milliseconds(500));
    }

    cout << "\n=== Motor test sequence completed ===" << endl;
}

int main() {
    // Set up signal handler for graceful shutdown
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);

    cout << "=== Two-Wheeled Car Motor Test ===" << endl;
    cout << "Press Ctrl+C to stop the program" << endl;

    try {
        // Setup GPIO
        setupGPIO();

        // Wait a moment for initialization
        this_thread::sleep_for(chrono::milliseconds(500));

        // Run motor tests
        testMotors();

        cout << "\nTests completed. Program will loop. Press Ctrl+C to exit." << endl;

        // Loop and repeat tests
        int loopCount = 0;
        while (running) {
            loopCount++;
            cout << "\n=== Loop " << loopCount << " ===" << endl;
            testMotors();

            // Longer pause between loops
            cout << "Waiting 5 seconds before next loop..." << endl;
            this_thread::sleep_for(chrono::seconds(5));
        }

    }
    catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
    }

    // Ensure motors are stopped before exit
    stopAllMotors();

    cout << "Program exited gracefully." << endl;
    return 0;
}