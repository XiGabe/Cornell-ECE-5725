#!/usr/bin/env python3
"""
two_collide_gpio.py - Two balls collide on the piTFT.
Exits when the button on GPIO 17 is pressed.
FIXED: Correctly handles collision to prevent "sticking".
"""
import os
import sys
import time
import math
import pygame
import RPi.GPIO as GPIO

# --- Constants ---
WIDTH, HEIGHT = 320, 240
BLACK = (0, 0, 0)
RED = (255, 80, 80)
BLUE = (80, 128, 255)
GPIO_QUIT_PIN = 17

def init_display():
    """Initializes Pygame for the piTFT display."""
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.putenv('SDL_FBDEV', '/dev/fb0')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.mouse.set_visible(False)
    return screen

def setup_gpio():
    """Sets up the GPIO button."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_QUIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- MODIFIED COLLISION LOGIC ---
def resolve_elastic_collision(b1, b2, radius):
    """
    Handles the physics of an elastic collision.
    This version separates positional correction from velocity change
    to prevent the "sticking" issue.
    """
    dx = b2['x'] - b1['x']
    dy = b2['y'] - b1['y']
    dist = math.hypot(dx, dy)
    
    if dist == 0: return

    # --- Step 1: Positional Correction ---
    # Unconditionally push balls apart if they are overlapping.
    # This is the key to fixing the "sticking" problem.
    overlap = 2 * radius - dist
    if overlap > 0:
        # Normal vector (from b1 to b2)
        nx, ny = dx / dist, dy / dist
        
        # Push them apart based on the overlap amount
        b1['x'] -= nx * overlap / 2
        b1['y'] -= ny * overlap / 2
        b2['x'] += nx * overlap / 2
        b2['y'] += ny * overlap / 2

    # --- Step 2: Velocity Change ---
    # Only change velocities if the balls are moving towards each other.
    # Recalculate normal after position correction for accuracy, though not strictly necessary here.
    nx, ny = dx / dist, dy / dist
    rel_vel_dot = (b1['vx'] - b2['vx']) * nx + (b1['vy'] - b2['vy']) * ny
    
    if rel_vel_dot < 0:
        # Exchange velocity components along the normal (for equal masses)
        b1['vx'] -= rel_vel_dot * nx
        b1['vy'] -= rel_vel_dot * ny
        b2['vx'] += rel_vel_dot * nx
        b2['vy'] += rel_vel_dot * ny

def main():
    """Main program loop."""
    setup_gpio()
    screen = init_display()
    clock = pygame.time.Clock()
    
    radius = 30
    balls = [
        {'x': WIDTH * 0.35, 'y': HEIGHT * 0.5, 'vx': 2.5, 'vy': 1.8, 'color': RED},
        {'x': WIDTH * 0.65, 'y': HEIGHT * 0.5, 'vx': -1.8, 'vy': -2.2, 'color': BLUE},
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        if not GPIO.input(GPIO_QUIT_PIN):
            print("Quit button pressed!")
            running = False
            time.sleep(0.2)

        for b in balls:
            b['x'] += b['vx']
            b['y'] += b['vy']
            
            if b['x'] - radius < 0:
                b['x'] = radius
                b['vx'] *= -1
            elif b['x'] + radius > WIDTH:
                b['x'] = WIDTH - radius
                b['vx'] *= -1
            
            if b['y'] - radius < 0:
                b['y'] = radius
                b['vy'] *= -1
            elif b['y'] + radius > HEIGHT:
                b['y'] = HEIGHT - radius
                b['vy'] *= -1

        dx = balls[1]['x'] - balls[0]['x']
        dy = balls[1]['y'] - balls[0]['y']
        if dx*dx + dy*dy <= (2*radius)**2:
            resolve_elastic_collision(balls[0], balls[1], radius)

        screen.fill(BLACK)
        for b in balls:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), radius)
        pygame.display.flip()
        
        clock.tick(60)

    print("Cleaning up GPIO...")
    GPIO.cleanup()
    pygame.quit()
    print("Exiting.")
    sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt, cleaning up...")
        GPIO.cleanup()
        pygame.quit()
        sys.exit(0)