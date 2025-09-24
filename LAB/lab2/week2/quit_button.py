#!/usr/bin/env python3
"""
quit_button.py - Single on-screen quit button using pygame (monitor or piTFT)
Requires pigame.py and pitft_touchscreen.py in the same directory for piTFT touch.
"""
import os
import sys
import time
import pygame

# Set True to run on piTFT; False to debug on HDMI monitor
USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
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

    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(0, HEIGHT-40, WIDTH, 40)

    bailout_deadline = time.time() + 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if button_rect.collidepoint(x, y):
                    running = False

        if time.time() > bailout_deadline:
            running = False

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, button_rect)
        label = font.render('QUIT', True, WHITE)
        label_pos = label.get_rect(center=button_rect.center)
        screen.blit(label, label_pos)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


