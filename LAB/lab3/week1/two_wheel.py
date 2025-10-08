# two_wheel.py
# Description: Implements control functions for Left and Right DC motors (servos) 
# controlled by six distinct physical buttons, as required by Lab 3, Step 2.

import RPi.GPIO as GPIO
import time
import signal
import sys

# --- Configuration ---
PWM_FREQUENCY_HZ = 50 
FULL_SPEED_DC = 99.0 
STOP_SPEED_DC = 0.0
BOUNCE_TIME_MS = 200 # Debounce time for button presses

# Define Motor Pin Structures (BCM mode) - ADJUST AS NEEDED
MOTOR_L_PINS = {'IN1': 5, 'IN2': 6, 'PWM': 26, 'name': 'Left'}
MOTOR_R_PINS = {'IN1': 20, 'IN2': 21, 'PWM': 16, 'name': 'Right'}

# Define Button Pin Structures (Input Pins) - ADJUST ALL PINS AS NEEDED
# Pins are configured with PULL_UP. Button press (connected to GND) means state goes LOW.
BUTTON_PINS = {
    'L_CW': 18,       # Left Servo Clockwise
    'L_STOP': 23,     # Left Servo Stop
    'L_CCW': 24,      # Left Servo Counter-Clockwise
    'R_CW': 25,       # Right Servo Clockwise
    'R_STOP': 12,     # Right Servo Stop
    'R_CCW': 13       # Right Servo Counter-Clockwise
}

# Global PWM objects
pwm_L = None
pwm_R = None

def cleanup_and_exit(signum=None, frame=None):
    """Stops motors and cleans up GPIO on exit."""
    global pwm_L, pwm_R
    print("\nStopping motors and cleaning up GPIO...")
    
    # 1. Stop PWM
    if pwm_L:
        pwm_L.stop()
    if pwm_R:
        pwm_R.stop()
        
    # 2. Cleanup
    GPIO.cleanup()
    print("GPIO cleanup complete. Program finished.")
    if signum is not None:
        sys.exit(0)

def setup_gpio():
    """Initializes all GPIO pins, PWM instances, and button inputs."""
    global pwm_L, pwm_R
    GPIO.setmode(GPIO.BCM)
    
    # 1. Motor Setup (Outputs)
    for motor in [MOTOR_L_PINS, MOTOR_R_PINS]:
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
            
    # 2. Button Setup (Inputs with Pull-Up)
    for pin in BUTTON_PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    print("GPIO setup complete. Motors and 6 Buttons are ready.")
    
def control_motor(motor_pins, direction, speed_dc):
    """Generic function to set the state of a single motor."""
    
    pwm_obj = pwm_L if motor_pins['name'] == 'Left' else pwm_R
    
    # Determine IN1 and IN2 states based on direction
    in1_state = GPIO.LOW
    in2_state = GPIO.LOW
    
    if direction == 'CW': 
        in1_state = GPIO.HIGH
        in2_state = GPIO.LOW
        mode = "CW"
    elif direction == 'CCW': 
        in1_state = GPIO.LOW
        in2_state = GPIO.HIGH
        mode = "CCW"
    elif direction == 'STOP': 
        # Using L, L is typically freewheeling stop.
        # H, H is a short brake (quick stop), but L, L is safer for simple stop.
        in1_state = GPIO.LOW
        in2_state = GPIO.LOW
        mode = "Stop (Freewheel)"
        
    # Apply direction and speed
    GPIO.output(motor_pins['IN1'], in1_state)
    GPIO.output(motor_pins['IN2'], in2_state)
    pwm_obj.ChangeDutyCycle(speed_dc)
    
    print(f"-> {motor_pins['name']} Motor: {mode} at {speed_dc}% DC")

# --- Motor Control Functions (Called by Button Handlers) ---
# These are the 6 required functions, ensuring they are independent actions.

def left_servo_clockwise():
    control_motor(MOTOR_L_PINS, 'CW', FULL_SPEED_DC)

def left_servo_stop():
    control_motor(MOTOR_L_PINS, 'STOP', STOP_SPEED_DC)

def left_servo_counter_clockwise():
    control_motor(MOTOR_L_PINS, 'CCW', FULL_SPEED_DC)

def right_servo_clockwise():
    control_motor(MOTOR_R_PINS, 'CW', FULL_SPEED_DC)

def right_servo_stop():
    control_motor(MOTOR_R_PINS, 'STOP', STOP_SPEED_DC)

def right_servo_counter_clockwise():
    control_motor(MOTOR_R_PINS, 'CCW', FULL_SPEED_DC)

# --- Button Handlers ---
# Each handler checks if the button state is LOW (pressed) and executes the corresponding function.

def button_handler_factory(action_func):
    """Creates a callback function that executes the action only on button press (falling edge)."""
    
    # We use a wrapper function to ensure the action is only called when the pin goes LOW
    # (since the event detector triggers on the transition, but the callback needs the final state check)
    def handler(channel):
        if GPIO.input(channel) == GPIO.LOW:
            action_func()
    return handler

if __name__ == '__main__':
    # Set up signal handling for a clean exit (e.g., Ctrl+C)
    signal.signal(signal.SIGINT, cleanup_and_exit) 
    
    try:
        setup_gpio()
        
        # Initial state is STOPPED
        left_servo_stop() 
        right_servo_stop()

        # 3. Attach Event Detection to Buttons
        print("\n--- Attaching 6 Button Event Detectors ---")
        
        # Left Motor Functions
        GPIO.add_event_detect(BUTTON_PINS['L_CW'], GPIO.FALLING, callback=button_handler_factory(left_servo_clockwise), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['L_STOP'], GPIO.FALLING, callback=button_handler_factory(left_servo_stop), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['L_CCW'], GPIO.FALLING, callback=button_handler_factory(left_servo_counter_clockwise), bouncetime=BOUNCE_TIME_MS)
        
        # Right Motor Functions
        GPIO.add_event_detect(BUTTON_PINS['R_CW'], GPIO.FALLING, callback=button_handler_factory(right_servo_clockwise), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['R_STOP'], GPIO.FALLING, callback=button_handler_factory(right_servo_stop), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['R_CCW'], GPIO.FALLING, callback=button_handler_factory(right_servo_counter_clockwise), bouncetime=BOUNCE_TIME_MS)

        
        print("Listening for button presses (Press Ctrl+C to exit)...")
        
        # Keep the main program running to listen for events
        while True:
            time.sleep(0.1) 

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        cleanup_and_exit()
        
    finally:
        cleanup_and_exit()
