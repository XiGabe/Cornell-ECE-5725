#!/usr/bin/env python3
"""
one_button.py - Single button GPIO test program
ECE 5725 Lab 1 Week 2
"""

import RPi.GPIO as GPIO
import time

# Set button GPIO pin (using BCM numbering)
BUTTON_PIN = 17  # One of the buttons on piTFT

def setup():
    """Initialize GPIO settings"""
    # Set GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)
    
    # Set button pin as input with internal pull-up resistor
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    try:
        # Initialize GPIO
        setup()
        print(f"Monitoring GPIO {BUTTON_PIN} for button press...")
        print("Press Ctrl+C to exit")
        
        while True:
            # Button is pressed when GPIO goes LOW (due to pull-up)
            if not GPIO.input(BUTTON_PIN):
                print(f"Button {BUTTON_PIN} has been pressed")
                # Add small delay to prevent button bounce
                time.sleep(0.2)
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        # Clean up GPIO settings
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == "__main__":
    main()