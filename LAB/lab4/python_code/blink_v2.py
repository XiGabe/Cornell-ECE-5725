#
# jfs9, blink test 
#
#  v1 - blink an LED 
#  v2: 10/20/2020 compute frequency
#      10/10/2021 - check
#       3/25/2022 - check
#
#
import time
import RPi.GPIO as GPIO
import sys
import subprocess   # to call echo

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...

GPIO.setup(13, GPIO.OUT) # set GPIO 13 as output to blink LED 

i = 0
interval = 0.0005
frequency = (1/(2*interval))
print ("interval = " + str(interval) + " sec")
print ("period = " + str(interval * 2) + " sec")
print ("frequency = " + str(frequency) + " Hz")


#while (i < 100000):
while (i < (frequency + frequency) ): # remain in loop for a while
    GPIO.output(13, GPIO.HIGH)
    time.sleep(interval)
    GPIO.output(13, GPIO.LOW)
    time.sleep(interval)
    i = i + 1

GPIO.cleanup()
