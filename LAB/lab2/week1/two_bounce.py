#!/usr/bin/env python3
"""
two_bounce.py - Two independent bouncing balls at different speeds
"""
import os
import sys
import time
import pygame

USE_TFT = True

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)

WIDTH, HEIGHT = 320, 240

def init_display():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    return screen

def main():
    screen = init_display()
    clock = pygame.time.Clock()
    radius = 12
    balls = [
        {'x': WIDTH//3, 'y': HEIGHT//3, 'vx': 3, 'vy': 2, 'color': RED},
        {'x': 2*WIDTH//3, 'y': 2*HEIGHT//3, 'vx': -2, 'vy': -3, 'color': BLUE},
    ]

    bailout_deadline = time.time() + 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if time.time() > bailout_deadline:
            running = False

        for b in balls:
            b['x'] += b['vx']
            b['y'] += b['vy']
            if b['x'] - radius < 0 or b['x'] + radius > WIDTH:
                b['vx'] = -b['vx']
            if b['y'] - radius < 0 or b['y'] + radius > HEIGHT:
                b['vy'] = -b['vy']

        screen.fill(BLACK)
        for b in balls:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), radius)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


