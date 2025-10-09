#!/usr/bin/env python3
"""
screen_coordinates.py - Displays tap coordinates and a quit button on the piTFT.
Meets Lab 2, Week 2 requirements including touch coordinate display, quit button,
physical bailout, and code timeout. Requires pigame.py & pitft_touchscreen.py.
"""
import os
import sys
import time
import pygame
import RPi.GPIO as GPIO

# --- Configuration ---
# Set to True when running on the actual piTFT.
USE_TFT = True
WIDTH, HEIGHT = 320, 240
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
# Physical bailout button (GPIO27 - standard piTFT button 4)
BAILOUT_PIN = 27

# --- Environment Setup ---
def setup_env():
    """Sets environment variables for piTFT display driver and input device."""
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon') # Use framebuffer console driver
        os.putenv('SDL_FBDEV', '/dev/fb1')     # Direct output to piTFT framebuffer
        os.putenv('SDL_MOUSEDRV', 'dummy')   # Dummy driver for mouse
        os.putenv('SDL_MOUSEDEV', '/dev/null') # Null device for mouse input
        os.putenv('DISPLAY', '')               # No X server display

def setup_gpio():
    """Sets up GPIO for the physical bailout button."""
    try:
        GPIO.setmode(GPIO.BCM)
        # Setup as input with pull-up resistor (button press pulls pin low)
        GPIO.setup(BAILOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return True
    except:
        # Fails silently if running on a non-Pi system or RPi.GPIO isn't available
        return False

# --- Main Function ---
def main():
    setup_env()
    # Note: pygame.init() must be called AFTER environment variables are set 
    pygame.init()

    # --- piTFT Touch Driver Initialization (Lab Requirement) ---
    pitft = None
    if USE_TFT:
        pygame.mouse.set_visible(False)
        try:
            # Import pigame (which imports pitft_touchscreen) 
            import pigame
            pitft = pigame.PiTft() # Create piTft object 
        except ImportError:
            # This will happen if pigame.py/pitft_touchscreen.py are missing 
            pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None, 28)
    big = pygame.font.Font(None, 36)

    # Quit button (Lab Requirement: single button at the bottom) 
    quit_rect = pygame.Rect(0, HEIGHT-40, WIDTH, 40)
    
    last_xy = None
    all_touches = []
    
    # Code time-out (Lab Requirement: 120 seconds for sufficient data collection) 
    bailout_deadline = time.time() + 120 
    gpio_available = setup_gpio()

    running = True
    
    while running:
        # Check physical bailout button (Lab Requirement) 
        if gpio_available and not GPIO.input(BAILOUT_PIN):
            print("Physical bailout button pressed - exiting")
            running = False
            break

        # Update pitft touch events (Required for evdev to Pygame conversion) 
        if pitft:
            pitft.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # MOUSEBUTTONUP event handles tap/click release
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                
                # Lab Requirement: Print to console
                print(f"Touch at {x}, {y}")
                
                # Lab Requirement: Collect and display coordinates 
                last_xy = (x, y)
                all_touches.append({'x': x, 'y': y})

                # Check if quit button pressed (Lab Requirement) 
                if quit_rect.collidepoint(x, y):
                    print("Quit button pressed - exiting")
                    running = False

        # Check timeout (Lab Requirement) 
        if time.time() > bailout_deadline:
            print("Timeout reached - exiting")
            running = False

        # --- Drawing ---
        screen.fill(BLACK)

        # Lab Requirement: Display current touch coordinates on screen 
        if last_xy:
            current_text = big.render(f"Touch at {last_xy[0]}, {last_xy[1]}", True, WHITE)
            screen.blit(current_text, (10, 30)) 

        # Draw quit button 
        pygame.draw.rect(screen, RED, quit_rect)
        label = font.render('QUIT', True, WHITE)
        screen.blit(label, label.get_rect(center=quit_rect.center))

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    # --- Cleanup and Data Summary (For Lab Report) ---
    
    # Print first 20 coordinates
    if len(all_touches) >= 20:
        print("\n--- First 20 touches---")
        for i, touch in enumerate(all_touches[:20], 1):
            print(f"Touch #{i}: ({touch['x']}, {touch['y']})")
        print("-------------------------------------------------------")
    else:
        print(f"\nTotal touches collected: {len(all_touches)}")
    
    if pitft:
        del pitft
        
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()