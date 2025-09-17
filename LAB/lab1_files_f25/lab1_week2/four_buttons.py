#!/usr/bin/env python3
"""
four_buttons.py - Four button GPIO test program
ECE 5725 Lab 1 Week 2
"""

import RPi.GPIO as GPIO
import time

# Define button GPIO pins (BCM numbering)
# Four buttons on piTFT
BUTTONS = {
    'BUTTON1': 17,
    'BUTTON2': 22,
    'BUTTON3': 23,
    'BUTTON4': 27
}

def setup():
    """Initialize GPIO settings"""
    # Set GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)
    
    # Set all button pins as inputs with internal pull-up resistors
    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    try:
        # Initialize GPIO
        setup()
        print("Monitoring all buttons for press...")
        print("Press Ctrl+C to exit")
        print("Press Button4 (GPIO 27) to quit the program")
        
        while True:
            # Check all buttons
            for button_name, pin in BUTTONS.items():
                if not GPIO.input(pin):
                    print(f"Button {pin} has been pressed")
                    
                    # Exit program if Button4 is pressed
                    if pin == BUTTONS['BUTTON4']:
                        print("Exiting program...")
                        return
                    
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