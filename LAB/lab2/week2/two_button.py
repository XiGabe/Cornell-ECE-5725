#!/usr/bin/env python3
"""
two_button.py - On-screen Start and Quit buttons; runs two_collide animation
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
"""
import os
import sys
import time
import pygame
import subprocess

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
    font = pygame.font.Font(None, 36)

    start_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    quit_rect = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)
    anim_proc = None
    bailout_deadline = time.time() + 60

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if start_rect.collidepoint(x, y):
                    if anim_proc is None or anim_proc.poll() is not None:
                        # Launch two_collide.py as a subprocess
                        anim_proc = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'two_collide.py')])
                elif quit_rect.collidepoint(x, y):
                    running = False
                else:
                    print(f"Touch at {x}, {y}")

        if time.time() > bailout_deadline:
            running = False

        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, start_rect)
        pygame.draw.rect(screen, RED, quit_rect)
        screen.blit(font.render('START', True, WHITE), font.render('START', True, WHITE).get_rect(center=start_rect.center))
        screen.blit(font.render('QUIT', True, WHITE), font.render('QUIT', True, WHITE).get_rect(center=quit_rect.center))
        pygame.display.flip()
        pygame.time.Clock().tick(30)

    if anim_proc and anim_proc.poll() is None:
        anim_proc.terminate()
        try:
            anim_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            anim_proc.kill()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


