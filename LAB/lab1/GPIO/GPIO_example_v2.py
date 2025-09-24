#
# jfs9, 2/10/2024 GPIO example python script
#
#              This example has an error.....
#
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...
# setup piTFT buttons
#                        V need this so that button doesn't 'float'!
#GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # This causes a problem....
    time.sleep(1.0) # sleep a bit...
    print ( "tick.." )
    if ( not GPIO.input(26) ):
        print (" ") 
        print ("Button 26 pressed....")
