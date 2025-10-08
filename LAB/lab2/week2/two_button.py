#!/usr/bin/env python3
"""
control_two_collide.py - Level 1/2 UI to control two_collide animation
Level 1: Start, Quit
Level 2: Pause/Restart, Faster, Slower, Back
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
ECE 5725 Lab 2 Week 2
"""
import os
import sys
import time
import math
import pygame
import RPi.GPIO as GPIO

# --- CONFIGURATION ---
USE_TFT = True  # Set to True for final piTFT run
WIDTH, HEIGHT = 320, 240
BAILOUT_PIN = 27 # Physical bailout button (GPIO27)

# Colors (Minimal set)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (220, 0, 0)
BLUE = (0, 128, 255)

# Animation Defaults
INITIAL_RADIUS = 25

# --- SETUP FUNCTIONS ---
def setup_env():
    """Sets environment variables for piTFT display."""
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        # Using /dev/fb1 as per Lab 2 instructions
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'dummy')
        os.putenv('SDL_MOUSEDEV', '/dev/null')
        os.putenv('DISPLAY', '')

def setup_gpio():
    """Sets up GPIO for the physical bailout button."""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BAILOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True
    except:
        return False

# --- COLLISION LOGIC (Adopted from your two_collide.py) ---
def resolve_elastic_collision(b1, b2, radius):
    """Handles the physics of an elastic collision and resolves overlap."""
    dx = b2['x'] - b1['x']
    dy = b2['y'] - b1['y']
    dist = math.hypot(dx, dy)
    
    if dist == 0: return

    # 1. Positional Correction
    overlap = 2 * radius - dist
    if overlap > 0:
        nx, ny = dx / dist, dy / dist
        b1['x'] -= nx * overlap / 2
        b1['y'] -= ny * overlap / 2
        b2['x'] += nx * overlap / 2
        b2['y'] += ny * overlap / 2

    # 2. Velocity Change
    nx, ny = dx / dist, dy / dist
    rel_vel_dot = (b1['vx'] - b2['vx']) * nx + (b1['vy'] - b2['vy']) * ny
    
    if rel_vel_dot < 0:
        b1['vx'] -= rel_vel_dot * nx
        b1['vy'] -= rel_vel_dot * ny
        b2['vx'] += rel_vel_dot * nx
        b2['vy'] += rel_vel_dot * ny

# --- ANIMATION CLASS ---
class TwoCollideControl:
    def __init__(self):
        self.radius = INITIAL_RADIUS
        self.balls = [
            {'x': WIDTH*0.35, 'y': HEIGHT*0.5, 'vx': 2.5, 'vy': 1.8, 'color': RED},
            {'x': WIDTH*0.65, 'y': HEIGHT*0.5, 'vx': -1.8, 'vy': -2.2, 'color': BLUE},
        ]
        self.pause = False
        self.speed_scale = 1.0

    def update(self):
        """Updates ball positions, handles boundary and ball-to-ball collision."""
        if self.pause:
            return
            
        r = self.radius
        
        # 1. Update Positions and Boundary Collisions
        for b in self.balls:
            b['x'] += b['vx'] * self.speed_scale
            b['y'] += b['vy'] * self.speed_scale

            # X-axis boundary
            if b['x'] - r < 0:
                b['x'] = r
                b['vx'] = -b['vx']
            elif b['x'] + r > WIDTH:
                b['x'] = WIDTH - r
                b['vx'] = -b['vx']
                
            # Y-axis boundary
            if b['y'] - r < 0:
                b['y'] = r
                b['vy'] = -b['vy']
            elif b['y'] + r > HEIGHT:
                b['y'] = HEIGHT - r
                b['vy'] = -b['vy']

        # 2. Ball-to-Ball Collision Check
        b1, b2 = self.balls
        dx = b2['x'] - b1['x']
        dy = b2['y'] - b1['y']
        if dx*dx + dy*dy <= (2*self.radius)*(2*self.radius):
            resolve_elastic_collision(b1, b2, self.radius)

    def draw(self, screen):
        """Draws the balls on the screen."""
        for b in self.balls:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), self.radius)

# --- MAIN LOGIC ---
def main():
    setup_env()
    pygame.init()

    # piTFT Touch Driver Initialization
    pitft = None
    last_xy = None
    if USE_TFT:
        pygame.mouse.set_visible(False)
        try:
            import pigame
            pitft = pigame.PiTft()
        except ImportError:
            pass
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None, 30)
    big = pygame.font.Font(None, 36)
    # Level 1 Buttons
    start_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    quit_rect  = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)

    mode = 'menu1'  # 'menu1' or 'play'
    anim = TwoCollideControl()
    clock = pygame.time.Clock()

    gpio_available = setup_gpio()
    bailout_deadline = time.time() + 300 # 5 minutes timeout

    running = True
    while running:
        current_time = time.time()

        # Check physical bailout button
        if gpio_available and not GPIO.input(BAILOUT_PIN):
            running = False
            break

        # Update piTFT touch events
        if pitft:
            pitft.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                    # Level 1: Start/Quit
                print(f"Touch at {x}, {y}")
                last_xy = (x, y)
                if start_rect.collidepoint(x, y):
                    mode = 'play'
                    # Reset animation state and speed when starting
                    anim = TwoCollideControl() 
                elif quit_rect.collidepoint(x, y):
                    running = False
                # Note: No coordinate display in Level 1 for simplicity/focus
            
        # Check timeout
        if current_time > bailout_deadline:
            running = False

        # --- DRAWING ---
        screen.fill(BLACK)

        if mode == 'menu1':
            # Draw Level 1 UI
            if last_xy:
                current_text = big.render(f"Touch at {last_xy[0]}, {last_xy[1]}", True, WHITE)
                screen.blit(current_text, (10, 30)) 

            # Buttons
            pygame.draw.rect(screen, GREEN, start_rect)
            pygame.draw.rect(screen, RED,   quit_rect)
            screen.blit(font.render('START', True, BLACK), font.render('START', True, BLACK).get_rect(center=start_rect.center))
            screen.blit(font.render('QUIT',  True, BLACK), font.render('QUIT',  True, BLACK).get_rect(center=quit_rect.center))
        
        else: # mode == 'play'
            # Update and draw animation (fills the screen space)
            anim.update()
            anim.draw(screen)

            # Draw Level 2 UI (placed at the bottom)
            # Buttons
            pygame.draw.rect(screen, GREEN, start_rect)
            pygame.draw.rect(screen, RED,   quit_rect)
            screen.blit(font.render('START', True, BLACK), font.render('START', True, BLACK).get_rect(center=start_rect.center))
            screen.blit(font.render('QUIT',  True, BLACK), font.render('QUIT',  True, BLACK).get_rect(center=quit_rect.center))

            

        pygame.display.flip()
        clock.tick(60)

    # --- CLEANUP ---
    if pitft:
        del pitft
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()