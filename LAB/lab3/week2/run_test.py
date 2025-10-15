# run_test.py
# Description: Implements an automated test sequence with a piTFT GUI,
# using the Lab 2 touch control method.
import RPi.GPIO as GPIO
import time
import signal
import sys
import os
import pygame
from collections import deque
import pigame
from pygame.locals import *

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
pitft = pigame.PiTft()

pygame.mouse.set_visible(False)
SCREEN_SIZE = (320, 240)
screen = pygame.display.set_mode(SCREEN_SIZE)
BG_COLOR = (0, 0, 0)

# --- Font, Color, GPIO, State, and UI Definitions ---
WHITE, RED, GREEN, BLUE = (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)
FONT_BIG = pygame.font.Font(None, 40)
FONT_MEDIUM = pygame.font.Font(None, 28)
FONT_SMALL = pygame.font.Font(None, 22)

PWM_FREQUENCY_HZ = 50 
FULL_SPEED_DC = 99.0 
STOP_SPEED_DC = 0.0
BOUNCE_TIME_MS = 300
MOTOR_L_PINS = {'IN1': 5, 'IN2': 6, 'PWM': 26, 'name': 'Left'}
MOTOR_R_PINS = {'IN1': 20, 'IN2': 21, 'PWM': 16, 'name': 'Right'}
PHYSICAL_QUIT_PIN = 24

pwm_L, pwm_R = None, None
start_time = time.time()
left_motor_state, right_motor_state = "Stopped", "Stopped"
left_history = deque([("Stopped", 0.0)], maxlen=3)
right_history = deque([("Stopped", 0.0)], maxlen=3)
program_state = 'IDLE' 
BUTTON_RECTS = {
    'start': pygame.Rect(20, 180, 120, 50),
    'quit': pygame.Rect(180, 180, 120, 50)
}

# --- Test Sequence Definition ---
def move_forward(): control_motor(MOTOR_L_PINS,'CW',FULL_SPEED_DC); control_motor(MOTOR_R_PINS,'CW',FULL_SPEED_DC)
def move_backward(): control_motor(MOTOR_L_PINS,'CCW',FULL_SPEED_DC); control_motor(MOTOR_R_PINS,'CCW',FULL_SPEED_DC)
def pivot_left(): control_motor(MOTOR_L_PINS,'CCW',FULL_SPEED_DC); control_motor(MOTOR_R_PINS,'CW',FULL_SPEED_DC)
def pivot_right(): control_motor(MOTOR_L_PINS,'CW',FULL_SPEED_DC); control_motor(MOTOR_R_PINS,'CCW',FULL_SPEED_DC)
def stop_all(): control_motor(MOTOR_L_PINS,'STOP',STOP_SPEED_DC); control_motor(MOTOR_R_PINS,'STOP',STOP_SPEED_DC)
TEST_SEQUENCE = [(move_forward,2),(stop_all,1),(move_backward,2),(stop_all,1),(pivot_left,2),(stop_all,1),(pivot_right,2),(stop_all,1)]
sequence_index = 0
last_action_time = 0

# --- Core Functions ---
def cleanup_and_exit(signum=None, frame=None):
    global pitft
    print("\nStopping motors and cleaning up...")
    stop_all()
    time.sleep(0.1)
    GPIO.cleanup()
    if 'pitft' in globals():
        del(pitft)
    pygame.quit()
    print("Cleanup complete. Program finished.")
    if isinstance(signum, int) or signum is None: sys.exit(0)

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
    GPIO.setup(PHYSICAL_QUIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PHYSICAL_QUIT_PIN, GPIO.FALLING, callback=cleanup_and_exit, bouncetime=BOUNCE_TIME_MS)
    print("GPIO setup complete.")

def control_motor(motor_pins, direction, speed_dc):
    global left_motor_state, right_motor_state, left_history, right_history
    pwm_obj = pwm_L if motor_pins['name'] == 'Left' else pwm_R
    in1_state, in2_state, mode_str = GPIO.LOW, GPIO.LOW, "Stopped"
    if direction == 'CW': in1_state, in2_state, mode_str = GPIO.HIGH, GPIO.LOW, "Clockwise"
    elif direction == 'CCW': in1_state, in2_state, mode_str = GPIO.LOW, GPIO.HIGH, "Counter-Clk"
    GPIO.output(motor_pins['IN1'], in1_state); GPIO.output(motor_pins['IN2'], in2_state)
    pwm_obj.ChangeDutyCycle(speed_dc)
    timestamp = round(time.time() - start_time, 1)
    if motor_pins['name'] == 'Left':
        if left_motor_state != mode_str: left_motor_state=mode_str; left_history.appendleft((mode_str,timestamp))
    else:
        if right_motor_state != mode_str: right_motor_state=mode_str; right_history.appendleft((mode_str,timestamp))

def draw_gui():
    screen.fill(BG_COLOR)
    screen.blit(FONT_BIG.render("Left Motor", True, WHITE), (20, 10))
    screen.blit(FONT_BIG.render("Right Motor", True, WHITE), (170, 10))
    screen.blit(FONT_MEDIUM.render(f"Now: {left_motor_state}", True, BLUE), (20, 50))
    screen.blit(FONT_MEDIUM.render(f"Now: {right_motor_state}", True, BLUE), (170, 50))
    for i,(s,t) in enumerate(list(left_history)): screen.blit(FONT_SMALL.render(f"{t}s:{s}",True,WHITE),(20,110+i*20))
    for i,(s,t) in enumerate(list(right_history)): screen.blit(FONT_SMALL.render(f"{t}s:{s}",True,WHITE),(170,110+i*20))
    if program_state=='RUNNING': pygame.draw.rect(screen,RED,BUTTON_RECTS['start']); btn_text=FONT_BIG.render("STOP",True,WHITE)
    elif program_state=='PAUSED': pygame.draw.rect(screen,GREEN,BUTTON_RECTS['start']); btn_text=FONT_BIG.render("Resume",True,BG_COLOR)
    else: pygame.draw.rect(screen,GREEN,BUTTON_RECTS['start']); btn_text=FONT_BIG.render("Start",True,BG_COLOR)
    screen.blit(btn_text,(btn_text.get_rect(center=BUTTON_RECTS['start'].center)))
    pygame.draw.rect(screen,WHITE,BUTTON_RECTS['quit']); quit_text=FONT_BIG.render("Quit",True,BG_COLOR)
    screen.blit(quit_text,(quit_text.get_rect(center=BUTTON_RECTS['quit'].center)))
    pygame.display.flip()
    
# --- Main Program ---
if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup_and_exit) 
    
    try:
        setup_gpio()
        print("Program started. Press 'Start' on screen to begin.")
        
        while True:
            current_time_ms = pygame.time.get_ticks()
            
            pitft.update()

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if BUTTON_RECTS['quit'].collidepoint(pos):
                        cleanup_and_exit(signum=0)
                    elif BUTTON_RECTS['start'].collidepoint(pos):
                        if program_state == 'IDLE': program_state = 'RUNNING'; sequence_index = -1; last_action_time = current_time_ms - 9999
                        elif program_state == 'RUNNING': program_state = 'PAUSED'; stop_all()
                        elif program_state == 'PAUSED': program_state = 'RUNNING'; last_action_time = current_time_ms

            if program_state == 'RUNNING':
                action, duration = TEST_SEQUENCE[sequence_index]
                if current_time_ms - last_action_time >= duration * 1000:
                    sequence_index = (sequence_index + 1) % len(TEST_SEQUENCE)
                    next_action, _ = TEST_SEQUENCE[sequence_index]
                    next_action()
                    last_action_time = current_time_ms
            
            draw_gui()
            time.sleep(0.05)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        cleanup_and_exit()