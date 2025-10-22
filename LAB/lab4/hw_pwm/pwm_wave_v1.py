#
# jfs9, 11/16/16 
#
#  v1 - test wave functions
#
#
import time
import RPi.GPIO as GPIO
import sys
import subprocess   # to call echo

import pigpio

pi_hw = pigpio.pi()   # connect to pi gpio daemon

pi_hw.set_mode(13, pigpio.OUTPUT) # Setup pin 13 as an output: IMPORTANT!

pi_hw.wave_clear()  # clear all waves from DMA
pi_hw.wave_add_serial(13, 300, b'\xFF\xA5')   # setup a sample wave (one character!)
#                      ^   ^
#                GPIO pin  ^
#                        bit rate
wave_id = pi_hw.wave_create()   # create the wave in DMA
print "wave_id = " + str(wave_id) # print wave ID

pi_hw.wave_add_serial(13, 300, b'\xAA')   # setup a sample wave (one character!)
wave_id = pi_hw.wave_create()   # create second wave in DMA
print "wave_id = " + str(wave_id)   # print ID of second wave
#pi_hw.wave_add_serial(13, 300, b'\xFF\x00')   # setup a sample wave (two characters!)

pi_hw.wave_send_repeat(wave_id)  # send the wave to a GPIO pin, and repeat....
#pi_hw.wave_send_once(wave_id)  # send the wave to a GPIO pin once....

time.sleep(20)

pi_hw.wave_tx_stop() # Stop waveform transmission
                     # without this, waveform keeps running even when program quits

pi_hw.stop() # close pi gpio  resources

