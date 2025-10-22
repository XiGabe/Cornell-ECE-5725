#
# jfs9, 10/2/15 Test pwm 
#
#  v1 - blink an LED 
#
#
import time
import RPi.GPIO as GPIO
import sys
import subprocess   # to call echo

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...

GPIO.setup(13, GPIO.OUT) # set GPIO 13 as output to blink LED 

i = 0
while (i < 10):
    GPIO.output(13, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(13, GPIO.LOW)
    time.sleep(0.5)
    i = i + 1

GPIO.cleanup()
