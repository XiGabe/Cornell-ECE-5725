#
# jfs9 2/10/2024  GPIO example python script
#
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)   # Set for GPIO (bcm) numbering not pin numbers...
# setup piTFT buttons
#                        V need this so that button doesn't 'float'!
#                        V   When button NOT pressed, this guarantees 
#                        V             signal = logical 1 = 3.3 Volts
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    time.sleep(0.2)  # Without sleep, no screen output!
    if ( not GPIO.input(26) ):
        print (" ") 
        print ("Button 26 pressed....")
