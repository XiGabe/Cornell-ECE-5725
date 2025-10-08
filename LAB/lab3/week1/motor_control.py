# motor_control.py
# Description: Cycles a single DC motor through stopped, half-speed, and full-speed in both CW and CCW directions.
# Each speed increment runs for 3 seconds.

import RPi.GPIO as GPIO
import time

# --- Configuration ---
# GPIO Pins (BCM mode) - ADJUST AS NEEDED
IN1_PIN = 5     # Connected to AIN1
IN2_PIN = 6     # Connected to AIN2
PWM_PIN = 26    # Connected to PWMA
STANDBY_PIN = 17 # Assuming a separate GPIO for STNDBY, or directly to 3.3V/5V.
                 # If connecting STNDBY directly to 3.3V/5V, this pin is not needed.

# Motor Control Parameters
PWM_FREQUENCY_HZ = 50 # Typical value for continuous rotation motor 
FULL_SPEED_DC = 99.0  # Use 100% duty cycle for full speed rotation (or 99% for safety) 
HALF_SPEED_DC = 50.0  # Experiment with 50% to 75% for half speed 
STOP_SPEED_DC = 0.0   # Set to zero to stop using PWM 
STEP_DURATION = 3.0   # Each speed increment runs for 3 seconds 

# Global PWM object reference
motor_pwm = None

def setup_gpio():
    """Initializes GPIO pins and the PWM instance."""
    global motor_pwm
    GPIO.setmode(GPIO.BCM)
    
    # Setup Direction Control Pins (Output)
    GPIO.setup(IN1_PIN, GPIO.OUT)
    GPIO.setup(IN2_PIN, GPIO.OUT)
    
    # Setup PWM Pin (Output)
    GPIO.setup(PWM_PIN, GPIO.OUT)
    
    # Setup Standby Pin (Output, assume we control it for safety)
    # If STNDBY is hardwired to 3.3V/5V, comment this out.
    # GPIO.setup(STANDBY_PIN, GPIO.OUT)
    # GPIO.output(STANDBY_PIN, GPIO.HIGH) # Enable the motor controller
    
    # Create and start PWM instance
    motor_pwm = GPIO.PWM(PWM_PIN, PWM_FREQUENCY_HZ)
    # When the program starts, the motor should be stopped 
    motor_pwm.start(STOP_SPEED_DC) 

def set_motor_state(in1_state, in2_state, duty_cycle, mode_name):
    """Sets the motor direction and speed."""
    global motor_pwm
    
    # Set Direction Pins
    GPIO.output(IN1_PIN, in1_state)
    GPIO.output(IN2_PIN, in2_state)
    
    # Change Speed/Duty Cycle 
    motor_pwm.ChangeDutyCycle(duty_cycle)

    # Print indication on the screen 
    print(f"Mode: {mode_name} | DC: {duty_cycle:.1f}% | IN1:{in1_state} IN2:{in2_state}")
    
    time.sleep(STEP_DURATION)

def run_motor_cycle():
    """Performs the full CW and CCW speed ranging cycle."""
    
    # --- Motor Direction Control Table (based on data sheet) --- 
    # CW:  IN1=H, IN2=L, PWM=H  -> OUT1=H, OUT2=L
    # CCW: IN1=L, IN2=H, PWM=H  -> OUT1=L, OUT2=H
    # Stop: IN1=L, IN2=L, PWM=H -> OUT1=OFF, OUT2=OFF

    # 1. Clockwise Sequence 
    print("\n--- Clockwise Sequence ---")
    
    # Start: Stopped
    set_motor_state(GPIO.LOW, GPIO.LOW, STOP_SPEED_DC, "Stopped (Start)") # Stop mode 

    # Half Speed CW
    set_motor_state(GPIO.HIGH, GPIO.LOW, HALF_SPEED_DC, "Clockwise (Half-Speed)")

    # Full Speed CW
    set_motor_state(GPIO.HIGH, GPIO.LOW, FULL_SPEED_DC, "Clockwise (Full-Speed)")
    
    # Intermediate: Stopped
    set_motor_state(GPIO.LOW, GPIO.LOW, STOP_SPEED_DC, "Stopped (Intermediate)")

    # 2. Counter-Clockwise Sequence 
    print("\n--- Counter-Clockwise Sequence ---")

    # Half Speed CCW
    set_motor_state(GPIO.LOW, GPIO.HIGH, HALF_SPEED_DC, "Counter-Clockwise (Half-Speed)")

    # Full Speed CCW
    set_motor_state(GPIO.LOW, GPIO.HIGH, FULL_SPEED_DC, "Counter-Clockwise (Full-Speed)")

    # 3. Return to Stopped State 
    set_motor_state(GPIO.LOW, GPIO.LOW, STOP_SPEED_DC, "Stopped (Final)")

if __name__ == '__main__':
    try:
        setup_gpio()
        run_motor_cycle()

    except KeyboardInterrupt:
        print("\nProgram stopped by user (Ctrl+C).")
        
    finally:
        # Stop PWM and cleanup
        if motor_pwm:
            motor_pwm.stop()
        GPIO.cleanup()
        print("GPIO cleanup complete. Program finished.")