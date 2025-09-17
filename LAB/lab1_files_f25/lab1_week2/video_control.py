#!/usr/bin/env python3
"""
video_control.py - Control video playback using piTFT buttons
ECE 5725 Lab 1 Week 2
"""

import RPi.GPIO as GPIO
import os
import time

# FIFO file path
FIFO_PATH = '/home/pi/ECE-5725-Everything/LAB/lab1_files_f25/lab1_week2/video_fifo'

# Button GPIO pin definitions (BCM numbering)
BUTTONS = {
    'PAUSE': {'pin': 17, 'command': 'pause'},      # Pause/Resume
    'FORWARD': {'pin': 22, 'command': 'seek 10'},  # Forward 10 seconds
    'REWIND': {'pin': 23, 'command': 'seek -10'},  # Rewind 10 seconds
    'QUIT': {'pin': 27, 'command': 'quit'}         # Exit
}

def setup():
    """Initialize GPIO and FIFO"""
    # Set GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)
    
    # Set all button pins as inputs with internal pull-up resistors
    for button in BUTTONS.values():
        GPIO.setup(button['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Create FIFO if it doesn't exist
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def send_command(command):
    """Send command to FIFO"""
    try:
        with open(FIFO_PATH, 'w') as fifo:
            fifo.write(command + '\n')
            fifo.flush()
    except Exception as e:
        print(f"Error sending command: {e}")

def main():
    try:
        # Initialize setup
        setup()
        print("Video control program started")
        print("Button functions:")
        for name, button in BUTTONS.items():
            print(f"{name} (GPIO {button['pin']}): {button['command']}")
        
        # Main loop
        while True:
            # Check all buttons
            for name, button in BUTTONS.items():
                if not GPIO.input(button['pin']):
                    print(f"Button {name} (GPIO {button['pin']}) pressed")
                    send_command(button['command'])
                    
                    # Exit program if quit command
                    if button['command'] == 'quit':
                        print("Exiting program...")
                        return
                    
                    # Prevent button bounce
                    time.sleep(0.2)
            
            # Short sleep to reduce CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Clean up GPIO settings
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == "__main__":
    main()