# two_wheel.py
# Description: Defines and demonstrates functions to control two DC motors (Left and Right servos)
# using separate direction (INx) and speed (PWMx) pins. Control is intended via physical buttons.

import RPi.GPIO as GPIO
import time

# --- Configuration ---
PWM_FREQUENCY_HZ = 50 # 
FULL_SPEED_DC = 99.0 
STOP_SPEED_DC = 0.0

# Define Motor Pin Structures for modularity (BCM mode)
# ADJUST ALL PINS AS NEEDED
MOTOR_L_PINS = {'IN1': 5, 'IN2': 6, 'PWM': 26, 'name': 'Left'}
MOTOR_R_PINS = {'IN1': 20, 'IN2': 21, 'PWM': 16, 'name': 'Right'}

# Global PWM objects
pwm_L = None
pwm_R = None

def setup_gpio():
    """Initializes all GPIO pins and PWM instances for both motors."""
    global pwm_L, pwm_R
    GPIO.setmode(GPIO.BCM)
    
    for motor in [MOTOR_L_PINS, MOTOR_R_PINS]:
        # Setup direction and PWM pins
        GPIO.setup(motor['IN1'], GPIO.OUT)
        GPIO.setup(motor['IN2'], GPIO.OUT)
        GPIO.setup(motor['PWM'], GPIO.OUT)
        
        # Ensure motor starts stopped
        GPIO.output(motor['IN1'], GPIO.LOW)
        GPIO.output(motor['IN2'], GPIO.LOW)
        
        # Create PWM instance
        pwm_instance = GPIO.PWM(motor['PWM'], PWM_FREQUENCY_HZ)
        pwm_instance.start(STOP_SPEED_DC)
        
        if motor['name'] == 'Left':
            pwm_L = pwm_instance
        else:
            pwm_R = pwm_instance

    print("GPIO setup complete. Motors are ready.")

def control_motor(motor_pins, direction, speed_dc):
    """Generic function to set the state of a single motor."""
    
    # Determine the correct PWM object
    pwm_obj = pwm_L if motor_pins['name'] == 'Left' else pwm_R
    
    # Determine IN1 and IN2 states based on direction (refer to TB6612FNG table) 
    in1_state = GPIO.LOW
    in2_state = GPIO.LOW
    
    if direction == 'CW': # Clockwise
        in1_state = GPIO.HIGH
        in2_state = GPIO.LOW
        mode = "CW"
    elif direction == 'CCW': # Counter-Clockwise
        in1_state = GPIO.LOW
        in2_state = GPIO.HIGH
        mode = "CCW"
    elif direction == 'STOP': # Stop / Short Brake (L, L, H/L or H, H, H/L) 
        # Using L, L for "Stop" mode for now 
        in1_state = GPIO.LOW
        in2_state = GPIO.LOW
        mode = "Stop"
        
    # Set direction and speed
    GPIO.output(motor_pins['IN1'], in1_state)
    GPIO.output(motor_pins['IN2'], in2_state)
    pwm_obj.ChangeDutyCycle(speed_dc)
    
    print(f"{motor_pins['name']} Motor: {mode} at {speed_dc}% DC")

# --- Required Button Functions for two_wheel.py---

def left_servo_clockwise():
    control_motor(MOTOR_L_PINS, 'CW', FULL_SPEED_DC)

def left_servo_stop():
    # Note: Implementing correct commands for servo stop is required
    control_motor(MOTOR_L_PINS, 'STOP', STOP_SPEED_DC)

def left_servo_counter_clockwise():
    control_motor(MOTOR_L_PINS, 'CCW', FULL_SPEED_DC)

def right_servo_clockwise():
    control_motor(MOTOR_R_PINS, 'CW', FULL_SPEED_DC)

def right_servo_stop():
    control_motor(MOTOR_R_PINS, 'STOP', STOP_SPEED_DC)

def right_servo_counter_clockwise():
    control_motor(MOTOR_R_PINS, 'CCW', FULL_SPEED_DC)

# --- Main execution loop for demonstration ---
def demo_motor_control():
    print("\n--- Running Two-Wheel Demo ---")
    print("Simulating button presses for demonstration.")
    
    # Left Servo Cycle
    print("\nLeft Motor Actions:")
    left_servo_clockwise()
    time.sleep(1)
    left_servo_counter_clockwise()
    time.sleep(1)
    left_servo_stop()
    time.sleep(1)
    
    # Right Servo Cycle
    print("\nRight Motor Actions:")
    right_servo_clockwise()
    time.sleep(1)
    right_servo_counter_clockwise()
    time.sleep(1)
    right_servo_stop()
    time.sleep(1)
    
    # Combined Action (e.g., Forward)
    print("\nCombined Action: Forward")
    left_servo_clockwise()
    right_servo_clockwise()
    time.sleep(2)
    
    # Combined Action (Stop)
    print("\nCombined Action: Stop")
    left_servo_stop()
    right_servo_stop()


if __name__ == '__main__':
    try:
        setup_gpio()
        demo_motor_control()
        print("\nDemo finished.")
        
    except KeyboardInterrupt:
        print("\nProgram stopped by user (Ctrl+C).")
        
    finally:
        # Stop PWM objects
        if pwm_L:
            pwm_L.stop()
        if pwm_R:
            pwm_R.stop()
            
        GPIO.cleanup()
        print("GPIO cleanup complete. Program finished.")