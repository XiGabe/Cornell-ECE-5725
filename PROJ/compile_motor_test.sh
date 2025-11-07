#!/bin/bash
# compile_motor_test.sh
# Script to compile the motor test program

echo "Compiling motor_test.cpp..."

# Compile with wiringPi library
g++ -Wall -o motor_test motor_test.cpp -lwiringPi -lpthread

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    echo "Run with: ./motor_test"
    echo "Make sure you have wiringPi installed and run with sudo if needed"
else
    echo "Compilation failed!"
    echo "Make sure wiringPi is installed: sudo apt-get install wiringPi"
fi