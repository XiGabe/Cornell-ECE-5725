#!/usr/bin/env python3
"""
bounce.py - Single ball bounce using pygame; works on monitor and piTFT
"""
import os
import sys
import time
import pygame

USE_TFT = False  # set True to force piTFT mode

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

WIDTH, HEIGHT = 320, 240

def init_display():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    return screen

def main():
    screen = init_display()
    clock = pygame.time.Clock()
    radius = 12
    x, y = WIDTH // 2, HEIGHT // 2
    vx, vy = 3, 2

    bailout_deadline = time.time() + 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # bail-out timer
        if time.time() > bailout_deadline:
            running = False

        x += vx
        y += vy
        if x - radius < 0 or x + radius > WIDTH:
            vx = -vx
        if y - radius < 0 or y + radius > HEIGHT:
            vy = -vy

        screen.fill(BLACK)
        pygame.draw.circle(screen, RED, (x, y), radius)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


