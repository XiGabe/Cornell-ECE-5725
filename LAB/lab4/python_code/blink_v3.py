#
# jfs9, blink test 
#
#  v1 - blink an LED 
#  v2: 10/20/2020 compute frequency
#      10/10/2021 - check
#       3/25/2022 - check
# v3 - one time run with input then loop forever, exit with ctrlc
#
import time
import RPi.GPIO as GPIO
prompt_text = "Enter a frequency: "

is_number = False

frequency = int(input("Enter a frequency: "))

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...
GPIO.setup(13, GPIO.OUT) # set GPIO 13 as output to blink LED 

period = 1/frequency
interval = period/2
print ("interval = " + str(interval) + " sec")
print ("period = " + str(interval * 2) + " sec")
print ("frequency = " + str(frequency) + " Hz")

while (True ): # loop until ctrl-c 
    GPIO.output(13, GPIO.HIGH)
    time.sleep(interval)
    GPIO.output(13, GPIO.LOW)
    time.sleep(interval)
GPIO.cleanup()
