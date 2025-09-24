#!/usr/bin/env python3
"""
Fixed-duration polling version to pair with perf measurements.
Runs for RUN_SECONDS then exits without requiring button presses.
"""
import RPi.GPIO as GPIO
import os
import time

FIFO_PATH = '/home/pi/ECE-5725-Everything/LAB/lab1_files_f25/lab1_week2/video_fifo'
RUN_SECONDS = 10.0
SLEEP_SEC = 0.2  # change between runs: 0.2, 0.02, 0.002, 0.0002, 0.00002, or 0

BUTTONS = {
    'PAUSE': 17,
    'FWD10': 22,
    'REW10': 23,
    'QUIT':  27,
    'FWD30': 26,
    'REW30': 5,
}

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def main():
    try:
        setup()
        t0 = time.time()
        while (time.time() - t0) < RUN_SECONDS:
            for pin in BUTTONS.values():
                _ = GPIO.input(pin)
            if SLEEP_SEC > 0:
                time.sleep(SLEEP_SEC)
        # exit cleanly
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()


