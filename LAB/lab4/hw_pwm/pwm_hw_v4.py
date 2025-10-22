#
# jfs9, 10/2/15 Test pwm 
#
#  v1 - just generate an output signal and measure on scope
#
#  v2 - try different speeds
#  v2_dma - try  different speeds
#  v3_pigpio - try  different speeds 10/2023
#  v4 - 4/1/2024
#
import time
import sys
import pigpio

#GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...

pi_hw = pigpio.pi()   # connect to pi gpio daemon

# pi_hw.hardware_PWM(13, 50, 75000)  # 50 hz, 7.5 % duty cycle (1.5 msec)
##pi_hw.hardware_PWM(13, 50, 500000)  # 50 hz, 50 % duty cycle 

#pi_hw.hardware_PWM(13, 1000000, 500000)  # 1 MHz 50 % duty cycle 
pi_hw.hardware_PWM(13,   250000, 500000)  # 500 khz 50 % duty cycle 

time.sleep(20)

pi_hw.hardware_PWM(13, 0, 0)  # 0 hz, 0 % duty cycle - stop the motor! 
pi_hw.stop() # close pi gpio PWM resources
