#!/usr/bin/env python3
"""
six_buttons.py - GPIO test for four piTFT buttons plus two external buttons
ECE 5725 Lab 2
"""

import RPi.GPIO as GPIO
import time

# BCM pin map: reuse piTFT 4 buttons + 2 external buttons (example GPIO26, GPIO5)
BUTTONS = {
    'TFT_BTN1': 17,   # piTFT
    'TFT_BTN2': 22,   # piTFT
    'TFT_BTN3': 23,   # piTFT
    'TFT_BTN4': 27,   # piTFT
    'EXT_BTN1': 26,   # external button on cobbler
    'EXT_BTN2': 12     # external button on cobbler
}

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    try:
        setup()
        print("Monitoring 6 buttons. Press TFT_BTN4 (GPIO 27) to quit.")
        while True:
            for name, pin in BUTTONS.items():
                if not GPIO.input(pin):
                    print(f"Button {name} (GPIO {pin}) pressed")
                    if pin == BUTTONS['TFT_BTN4']:
                        print("Exiting...")
                        return
                    time.sleep(0.5)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == '__main__':
    main()


