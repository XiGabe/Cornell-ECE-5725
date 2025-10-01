#!/usr/bin/env python3
"""
more_video_control.py - Extend Lab1 video control with two extra buttons
Functions: pause/resume, ±10s, quit, and ±30s via two external buttons
ECE 5725 Lab 2
"""

import RPi.GPIO as GPIO
import os
import time

FIFO_PATH = "video_fifo"
# Map buttons to mplayer slave commands
BUTTONS = {
    'PAUSE':      {'pin': 17, 'command': 'pause'},
    'FORWARD10':  {'pin': 22, 'command': 'seek 10'},
    'REWIND10':   {'pin': 23, 'command': 'seek -10'},
    'QUIT':       {'pin': 27, 'command': 'quit'},
    # External buttons for ±30s
    'FORWARD30':  {'pin': 26, 'command': 'seek 30'},
    'REWIND30':   {'pin': 12,  'command': 'seek -30'},
}

def setup():
    GPIO.setmode(GPIO.BCM)
    for button in BUTTONS.values():
        GPIO.setup(button['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def send_command(command: str):
    try:
        with open(FIFO_PATH, 'w') as fifo:
            fifo.write(command + '\n')
            fifo.flush()
    except Exception as e:
        print(f"Error sending command: {e}")

def main():
    try:
        setup()
        print("more_video_control running. Press QUIT to exit.")
        while True:
            for name, button in BUTTONS.items():
                if not GPIO.input(button['pin']):
                    print(f"{name} pressed -> {button['command']}" + '\n')
                    send_command(button['command'])
                    if name == 'QUIT':
                        print("Exiting...")
                        return
                    time.sleep(0.2)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == '__main__':
    main()


