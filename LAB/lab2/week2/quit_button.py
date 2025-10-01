#!/usr/bin/env python3
"""
quit_button.py - Single on-screen quit button using pygame (monitor or piTFT)
Requires pigame.py and pitft_touchscreen.py in the same directory for piTFT touch.
ECE 5725 Lab 2 Week 2
"""
import os
import sys
import time
import pygame
import RPi.GPIO as GPIO

# Set True to run on piTFT; False to debug on HDMI monitor
USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)

WIDTH, HEIGHT = 320, 240

# Physical bailout button (GPIO27 - piTFT button 4)
BAILOUT_PIN = 27

def setup_env():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'dummy')
        os.putenv('SDL_MOUSEDEV', '/dev/null')
        os.putenv('DISPLAY', '')

def setup_gpio():
    """Setup physical bailout button"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BAILOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True
    except:
        print("GPIO setup failed - running without physical bailout button")
        return False

def main():
    setup_env()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    if USE_TFT:
        pygame.mouse.set_visible(False)
        # Import pigame for piTFT touch support
        try:
            import pigame
            pitft = pigame.PiTft()
        except ImportError:
            print("Warning: pigame module not found - touch may not work on piTFT")
            pitft = None
    else:
        pitft = None

    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(0, HEIGHT-40, WIDTH, 40)

    # Setup GPIO for physical bailout button
    gpio_available = setup_gpio()

    # Timeouts - 30 seconds for initial testing, can be increased
    bailout_deadline = time.time() + 30

    running = True
    while running:
        # Check physical bailout button
        if gpio_available and not GPIO.input(BAILOUT_PIN):
            print("Physical bailout button pressed. End this program.")
            running = False
            break

        # Update pitft if available
        if pitft:
            pitft.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                print(f"Touch at {x}, {y}")
                if button_rect.collidepoint(x, y):
                    print("Quit button pressed")
                    running = False

        # Check timeout
        if time.time() > bailout_deadline:
            print("Timeout reached")
            running = False

        # Draw screen
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, button_rect)
        label = font.render('QUIT', True, WHITE)
        label_pos = label.get_rect(center=button_rect.center)
        screen.blit(label, label_pos)
        pygame.display.flip()

        # Control frame rate
        pygame.time.Clock().tick(30)

    # Cleanup
    if pitft:
        del pitft
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


