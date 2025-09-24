#!/usr/bin/env python3
"""
screen_coordinates.py - Show coordinates of taps/clicks and a quit button.
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
"""
import os
import sys
import time
import pygame

USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (220, 0, 0)

WIDTH, HEIGHT = 320, 240

def setup_env():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'dummy')
        os.putenv('SDL_MOUSEDEV', '/dev/null')
        os.putenv('DISPLAY', '')

def main():
    setup_env()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    if USE_TFT:
        pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, 28)
    big = pygame.font.Font(None, 36)

    quit_rect = pygame.Rect(0, HEIGHT-40, WIDTH, 40)
    last_xy = None
    bailout_deadline = time.time() + 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                x, y = pygame.mouse.get_pos()
                print(f"Touch at {x}, {y}")
                last_xy = (x, y)
                if event.type == pygame.MOUSEBUTTONUP and quit_rect.collidepoint(x, y):
                    running = False

        if time.time() > bailout_deadline:
            running = False

        screen.fill(BLACK)
        if last_xy:
            msg = big.render(f"Touch at {last_xy[0]}, {last_xy[1]}", True, WHITE)
            screen.blit(msg, (10, 10))
        pygame.draw.rect(screen, RED, quit_rect)
        label = font.render('QUIT', True, WHITE)
        screen.blit(label, label.get_rect(center=quit_rect.center))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


