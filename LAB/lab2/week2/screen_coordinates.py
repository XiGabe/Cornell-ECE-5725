#!/usr/bin/env python3
"""
screen_coordinates.py - Show coordinates of taps/clicks and a quit button.
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
Collects coordinate data for lab report analysis.
ECE 5725 Lab 2 Week 2
"""
import os
import sys
import time
import pygame
import RPi.GPIO as GPIO
from datetime import datetime

USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (220, 0, 0)
BLUE = (0, 128, 255)
YELLOW = (255, 255, 0)

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

    font = pygame.font.Font(None, 28)
    big = pygame.font.Font(None, 36)
    small = pygame.font.Font(None, 20)

    # Quit button at bottom
    quit_rect = pygame.Rect(0, HEIGHT-40, WIDTH, 40)

    # Touch history for display
    touch_history = []
    max_history = 5

    # Data collection for lab report
    all_touches = []

    # Current touch position
    last_xy = None

    # Setup GPIO for physical bailout button
    gpio_available = setup_gpio()

    # Longer timeout for coordinate collection (2 minutes)
    bailout_deadline = time.time() + 120

    running = True
    touch_count = 0

    print("Screen Coordinates Test Started")
    print("Tap anywhere on screen to see coordinates")
    print("Press QUIT button or GPIO27 to exit")
    print(f"Screen dimensions: {WIDTH}x{HEIGHT}")
    print(f"Corner coordinates: (0,0) top-left, ({WIDTH},{HEIGHT}) bottom-right")
    print("-" * 50)

    while running:
        # Check physical bailout button
        if gpio_available and not GPIO.input(BAILOUT_PIN):
            print("Physical bailout button pressed - exiting")
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
                touch_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                # Print to console
                print(f"Touch #{touch_count} at ({x}, {y}) - {timestamp}")

                # Add to collections
                touch_data = {'x': x, 'y': y, 'time': timestamp, 'count': touch_count}
                all_touches.append(touch_data)
                touch_history.append(touch_data)

                # Keep only recent touches for display
                if len(touch_history) > max_history:
                    touch_history.pop(0)

                last_xy = (x, y)

                # Check if quit button pressed
                if quit_rect.collidepoint(x, y):
                    print("Quit button pressed - exiting")
                    running = False

        # Check timeout
        if time.time() > bailout_deadline:
            print("Timeout reached - exiting")
            running = False

        # Clear screen
        screen.fill(BLACK)

        # Draw grid lines for reference
        pygame.draw.line(screen, (40, 40, 40), (WIDTH//2, 0), (WIDTH//2, HEIGHT-40), 1)
        pygame.draw.line(screen, (40, 40, 40), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)

        # Draw corner labels
        corner_labels = [
            (0, 0, "(0,0)"),
            (WIDTH-60, 0, f"({WIDTH},0)"),
            (0, 15, f"(0,{HEIGHT})"),
            (WIDTH-80, 15, f"({WIDTH},{HEIGHT})")
        ]
        for x, y, label in corner_labels:
            text = small.render(label, True, YELLOW)
            screen.blit(text, (x, y))

        # Display current touch coordinates
        if last_xy:
            current_text = big.render(f"Touch at {last_xy[0]}, {last_xy[1]}", True, WHITE)
            screen.blit(current_text, (10, 30))

            # Draw a marker at the touch position
            pygame.draw.circle(screen, GREEN, last_xy, 5)
            pygame.draw.circle(screen, WHITE, last_xy, 5, 1)

        # Display recent touch history
        y_offset = 70
        history_text = small.render("Recent touches:", True, BLUE)
        screen.blit(history_text, (10, y_offset))
        y_offset += 25

        for touch in touch_history[-3:]:  # Show last 3 touches
            text = small.render(f"#{touch['count']}: ({touch['x']}, {touch['y']})", True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 20

        # Display touch count
        count_text = font.render(f"Total touches: {len(all_touches)}", True, GREEN)
        screen.blit(count_text, (10, HEIGHT-55))

        # Draw quit button
        pygame.draw.rect(screen, RED, quit_rect)
        label = font.render('QUIT', True, WHITE)
        screen.blit(label, label.get_rect(center=quit_rect.center))

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    # Print summary before exit
    print("\n" + "=" * 50)
    print("TOUCH COORDINATE SUMMARY")
    print("=" * 50)
    print(f"Total touches collected: {len(all_touches)}")
    print(f"Screen coverage: X range {min([t['x'] for t in all_touches]) if all_touches else 0}-{max([t['x'] for t in all_touches]) if all_touches else 0}, Y range {min([t['y'] for t in all_touches]) if all_touches else 0}-{max([t['y'] for t in all_touches]) if all_touches else 0}")
    print("\nAll touch coordinates:")
    for i, touch in enumerate(all_touches, 1):
        print(f"{i:2d}. ({touch['x']:3d}, {touch['y']:3d}) at {touch['time']}")

    if len(all_touches) >= 20:
        print(f"\nFirst 20 touches for lab report:")
        for i, touch in enumerate(all_touches[:20], 1):
            print(f"{i:2d}. ({touch['x']:3d}, {touch['y']:3d})")
    else:
        print(f"\nCollected {len(all_touches)} touches (need 20 for complete lab report)")

    # Cleanup
    if pitft:
        del pitft
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


