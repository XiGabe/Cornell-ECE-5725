#!/usr/bin/env python3
"""
more_video_control_cb.py - Simplified Interrupt (callback) version of video controller
ECE 5725 Lab 2
"""

import RPi.GPIO as GPIO
import os
import time
import sys

FIFO_PATH = 'video_fifo'

PAUSE_PIN = 17
FORWARD10_PIN = 22
REWIND10_PIN = 23
QUIT_PIN = 27
FORWARD30_PIN = 26
REWIND30_PIN = 12

def send_command(command: str):
    """Sends a command to the video player via a named pipe."""
    try:
        with open(FIFO_PATH, 'w') as fifo:
            fifo.write(command + '\n')
            fifo.flush()
    except Exception as e:
        print(f"Error sending command: {e}")

def pause_callback(channel):
    print("send pause To Fifo")
    send_command('pause')

def forward10_callback(channel):
    print("send seek 10 to Fifo")
    send_command('seek 10')

def rewind10_callback(channel):
    print("send seek -10 to Fifo")
    send_command('seek -10')

def quit_callback(channel):
    print("send quit to Fifo")
    send_command('quit')
    sys.exit(0)

def forward30_callback(channel):
    print("send seek 30 to Fifo")
    send_command('seek 30')

def rewind30_callback(channel):
    print("send seek -30 to Fifo")
    send_command('seek -30')

def setup():
    """Sets up GPIO pins and event detection."""
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(PAUSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PAUSE_PIN, GPIO.FALLING, callback=pause_callback, bouncetime=200)

    GPIO.setup(FORWARD10_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(FORWARD10_PIN, GPIO.FALLING, callback=forward10_callback, bouncetime=200)

    GPIO.setup(REWIND10_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(REWIND10_PIN, GPIO.FALLING, callback=rewind10_callback, bouncetime=200)

    GPIO.setup(QUIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(QUIT_PIN, GPIO.FALLING, callback=quit_callback, bouncetime=200)

    GPIO.setup(FORWARD30_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(FORWARD30_PIN, GPIO.FALLING, callback=forward30_callback, bouncetime=200)

    GPIO.setup(REWIND30_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(REWIND30_PIN, GPIO.FALLING, callback=rewind30_callback, bouncetime=200)
    
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def main():
    """Main execution loop."""
    try:
        setup()
        print("more_video_control_cb running. Press QUIT button to stop.")
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed")

if __name__ == '__main__':
    main()