# rolling_control_touch.py
# Description: Integrates motor control with a piTFT GUI, using the Lab 2
# touch control method (evdev + pigame).

import RPi.GPIO as GPIO
import time
import signal
import sys
import os
import pygame
from collections import deque
import pigame
from pygame.locals import *

# Set environment variables for piTFT display and touch functionality
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV','dummy') 
os.putenv('SDL_MOUSEDEV','/dev/null')
os.putenv('DISPLAY','')

pygame.init()

# (Lab 2) Create a PiTft object to handle touch events
pitft = pigame.PiTft()

# Screen properties
SCREEN_SIZE = (320, 240)
screen = pygame.display.set_mode(SCREEN_SIZE)
BG_COLOR = (0, 0, 0) # Black
pygame.mouse.set_visible(False)
# --- Font and Color Definitions ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0) # Changed GREEN to be more visible
BLUE = (0, 0, 255)
FONT_BIG = pygame.font.Font(None, 40)
FONT_MEDIUM = pygame.font.Font(None, 28)
FONT_SMALL = pygame.font.Font(None, 22)

# --- GPIO Configuration ---
PWM_FREQUENCY_HZ = 50 
FULL_SPEED_DC = 99.0 
STOP_SPEED_DC = 0.0
BOUNCE_TIME_MS = 200

MOTOR_L_PINS = {'IN1': 5, 'IN2': 6, 'PWM': 26, 'name': 'Left'}
MOTOR_R_PINS = {'IN1': 20, 'IN2': 21, 'PWM': 16, 'name': 'Right'}

BUTTON_PINS = {
    'L_CW': 17, 'L_STOP': 22, 'L_CCW': 23,
    'R_CW': 27, 'R_STOP': 12, 'R_CCW': 13
}

# Global PWM objects
pwm_L, pwm_R = None, None

# --- State Management ---
start_time = time.time()
left_motor_state = "Stopped"
right_motor_state = "Stopped"
left_history = deque([("Stopped", 0.0)], maxlen=3)
right_history = deque([("Stopped", 0.0)], maxlen=3)
panic_mode = False

# --- UI Layout ---
BUTTON_RECTS = {
    'panic_stop': pygame.Rect(20, 180, 120, 50),
    'quit': pygame.Rect(180, 180, 120, 50)
}

# --- Core Functions ---
def cleanup_and_exit(signum=None, frame=None):
    """Stops motors, cleans up GPIO, and quits Pygame on exit."""
    global pitft
    print("\nStopping motors and cleaning up...")
    if 'pwm_L' in globals() and pwm_L: pwm_L.stop()
    if 'pwm_R' in globals() and pwm_R: pwm_R.stop()
    GPIO.cleanup()
    
    if 'pitft' in globals():
        del(pitft)
        
    pygame.quit()
    print("Cleanup complete. Program finished.")
    if signum is not None: sys.exit(0)

def setup_gpio():
    global pwm_L, pwm_R
    GPIO.setmode(GPIO.BCM)
    for motor in [MOTOR_L_PINS, MOTOR_R_PINS]:
        GPIO.setup([motor['IN1'], motor['IN2'], motor['PWM']], GPIO.OUT)
        GPIO.output([motor['IN1'], motor['IN2']], GPIO.LOW)
        pwm_instance = GPIO.PWM(motor['PWM'], PWM_FREQUENCY_HZ)
        pwm_instance.start(STOP_SPEED_DC)
        if motor['name'] == 'Left': pwm_L = pwm_instance
        else: pwm_R = pwm_instance
    for pin in BUTTON_PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("GPIO setup complete.")

def control_motor(motor_pins, direction, speed_dc):
    global left_motor_state, right_motor_state, left_history, right_history
    if panic_mode and direction != 'STOP': return
    pwm_obj = pwm_L if motor_pins['name'] == 'Left' else pwm_R
    in1_state, in2_state, mode_str = GPIO.LOW, GPIO.LOW, "Stopped"
    if direction == 'CW': in1_state, in2_state, mode_str = GPIO.HIGH, GPIO.LOW, "Clockwise"
    elif direction == 'CCW': in1_state, in2_state, mode_str = GPIO.LOW, GPIO.HIGH, "Counter-Clk"
    GPIO.output(motor_pins['IN1'], in1_state)
    GPIO.output(motor_pins['IN2'], in2_state)
    pwm_obj.ChangeDutyCycle(speed_dc)
    timestamp = round(time.time() - start_time, 1)
    if motor_pins['name'] == 'Left':
        if left_motor_state != mode_str:
            left_motor_state = mode_str
            left_history.appendleft((mode_str, timestamp))
    else:
        if right_motor_state != mode_str:
            right_motor_state = mode_str
            right_history.appendleft((mode_str, timestamp))

# --- Specific Motor Actions and Button Callbacks ---
def left_servo_clockwise(): control_motor(MOTOR_L_PINS, 'CW', FULL_SPEED_DC)
def left_servo_stop(): control_motor(MOTOR_L_PINS, 'STOP', STOP_SPEED_DC)
def left_servo_counter_clockwise(): control_motor(MOTOR_L_PINS, 'CCW', FULL_SPEED_DC)
def right_servo_clockwise(): control_motor(MOTOR_R_PINS, 'CW', FULL_SPEED_DC)
def right_servo_stop(): control_motor(MOTOR_R_PINS, 'STOP', STOP_SPEED_DC)
def right_servo_counter_clockwise(): control_motor(MOTOR_R_PINS, 'CCW', FULL_SPEED_DC)

def button_handler_factory(action_func):
    def handler(channel):
        if GPIO.input(channel) == GPIO.LOW: action_func()
    return handler

# --- GUI Drawing Function ---
def draw_gui():
    screen.fill(BG_COLOR)
    screen.blit(FONT_BIG.render("Left Motor", True, WHITE), (20, 10))
    screen.blit(FONT_BIG.render("Right Motor", True, WHITE), (160, 10))
    screen.blit(FONT_MEDIUM.render(f"{left_motor_state}", True, BLUE), (20, 50))
    screen.blit(FONT_MEDIUM.render(f"{right_motor_state}", True, BLUE), (170, 50))
    screen.blit(FONT_MEDIUM.render("History:", True, WHITE), (20, 80))
    screen.blit(FONT_MEDIUM.render("History:", True, WHITE), (170, 80))
    for i, (state, ts) in enumerate(list(left_history)):
        screen.blit(FONT_SMALL.render(f"{ts}s: {state}", True, WHITE), (20, 110 + i * 20))
    for i, (state, ts) in enumerate(list(right_history)):
        screen.blit(FONT_SMALL.render(f"{ts}s: {state}", True, WHITE), (170, 110 + i * 20))
    if panic_mode:
        pygame.draw.rect(screen, GREEN, BUTTON_RECTS['panic_stop'])
        btn_text = FONT_BIG.render("Resume", True, BG_COLOR)
    else:
        pygame.draw.rect(screen, RED, BUTTON_RECTS['panic_stop'])
        btn_text = FONT_BIG.render("STOP", True, WHITE)
    screen.blit(btn_text, (btn_text.get_rect(center=BUTTON_RECTS['panic_stop'].center)))
    pygame.draw.rect(screen, WHITE, BUTTON_RECTS['quit'])
    quit_text = FONT_BIG.render("Quit", True, BG_COLOR)
    screen.blit(quit_text, (quit_text.get_rect(center=BUTTON_RECTS['quit'].center)))
    pygame.display.flip()

# --- Main Program ---
if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup_and_exit) 
    
    try:
        setup_gpio()
        # Attach GPIO event detectors for all 6 buttons
        GPIO.add_event_detect(BUTTON_PINS['L_CW'], GPIO.FALLING, callback=button_handler_factory(left_servo_clockwise), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['L_STOP'], GPIO.FALLING, callback=button_handler_factory(left_servo_stop), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['L_CCW'], GPIO.FALLING, callback=button_handler_factory(left_servo_counter_clockwise), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['R_CW'], GPIO.FALLING, callback=button_handler_factory(right_servo_clockwise), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['R_STOP'], GPIO.FALLING, callback=button_handler_factory(right_servo_stop), bouncetime=BOUNCE_TIME_MS)
        GPIO.add_event_detect(BUTTON_PINS['R_CCW'], GPIO.FALLING, callback=button_handler_factory(right_servo_counter_clockwise), bouncetime=BOUNCE_TIME_MS)

        print("Listening for button presses and screen touches...")
        
        while True:
            pitft.update()
            # Scan for Pygame events (which now include touch) 
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if BUTTON_RECTS['quit'].collidepoint(pos):
                        cleanup_and_exit(signum=0)
                    elif BUTTON_RECTS['panic_stop'].collidepoint(pos):
                        panic_mode = not panic_mode
                        if panic_mode:
                            print("PANIC STOP ACTIVATED")
                            control_motor(MOTOR_L_PINS, 'STOP', STOP_SPEED_DC)
                            control_motor(MOTOR_R_PINS, 'STOP', STOP_SPEED_DC)
                        else:
                            print("Resume pressed.")
            
            draw_gui()
            time.sleep(0.2)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        cleanup_and_exit()