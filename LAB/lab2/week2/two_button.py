#!/usr/bin/env python3
"""
two_button.py - On-screen Start and Quit buttons; runs two_collide animation
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
ECE 5725 Lab 2 Week 2
"""
import os
import sys
import time
import pygame
import subprocess
import RPi.GPIO as GPIO

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

    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Button layout - positioned to avoid interference with animation
    start_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    quit_rect = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)

    # Animation subprocess management
    anim_proc = None
    anim_status = "Ready"

    # Setup GPIO for physical bailout button
    gpio_available = setup_gpio()

    # Longer timeout for demonstration
    bailout_deadline = time.time() + 180  # 3 minutes

    # Touch coordinate display
    last_touch = None
    touch_display_time = 0

    print("Two Button Interface Started")
    print("Buttons: START (launches two_collide.py), QUIT (exits)")
    print("Physical bailout: GPIO27 button")
    print("-" * 50)

    running = True
    clock = pygame.time.Clock()

    while running:
        current_time = time.time()

        # Check physical bailout button
        if gpio_available and not GPIO.input(BAILOUT_PIN):
            print("Physical bailout button pressed - exiting")
            running = False
            break

        # Update pitft if available
        if pitft:
            pitft.update()

        # Clear touch display after 2 seconds
        if last_touch and current_time - touch_display_time > 2.0:
            last_touch = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                last_touch = (x, y)
                touch_display_time = current_time

                if start_rect.collidepoint(x, y):
                    # Check if animation is already running
                    if anim_proc is None or anim_proc.poll() is not None:
                        print("Starting two_collide.py animation...")
                        try:
                            # Find two_collide.py in week1 directory
                            anim_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'week1', 'two_collide.py')
                            if not os.path.exists(anim_path):
                                anim_path = os.path.join(os.path.dirname(__file__), 'two_collide.py')

                            if os.path.exists(anim_path):
                                anim_proc = subprocess.Popen([sys.executable, anim_path])
                                anim_status = "Running"
                                print(f"Animation started (PID: {anim_proc.pid})")
                            else:
                                print("Error: two_collide.py not found")
                                anim_status = "Error"
                        except Exception as e:
                            print(f"Error starting animation: {e}")
                            anim_status = "Error"
                    else:
                        print("Animation already running")
                        anim_status = "Already Running"
                elif quit_rect.collidepoint(x, y):
                    print("Quit button pressed - exiting")
                    running = False
                else:
                    print(f"Touch at ({x}, {y}) - outside buttons")

        # Check animation status
        if anim_proc and anim_proc.poll() is not None:
            anim_status = "Stopped"
            print("Animation stopped")

        # Check timeout
        if current_time > bailout_deadline:
            print("Timeout reached - exiting")
            running = False

        # Draw screen
        screen.fill(BLACK)

        # Draw title
        title_text = font.render("Two Collide Control", True, WHITE)
        title_rect = title_text.get_rect(centerx=WIDTH//2, y=10)
        screen.blit(title_text, title_rect)

        # Draw status
        status_color = GREEN if anim_status == "Running" else YELLOW if anim_status == "Ready" else RED
        status_text = small_font.render(f"Animation: {anim_status}", True, status_color)
        screen.blit(status_text, (10, 50))

        # Draw buttons
        pygame.draw.rect(screen, GREEN, start_rect)
        pygame.draw.rect(screen, RED, quit_rect)

        # Button labels
        start_label = font.render('START', True, WHITE)
        start_label_rect = start_label.get_rect(center=start_rect.center)
        screen.blit(start_label, start_label_rect)

        quit_label = font.render('QUIT', True, WHITE)
        quit_label_rect = quit_label.get_rect(center=quit_rect.center)
        screen.blit(quit_label, quit_label_rect)

        # Display last touch coordinates
        if last_touch:
            touch_text = small_font.render(f"Touch: ({last_touch[0]}, {last_touch[1]})", True, BLUE)
            screen.blit(touch_text, (10, HEIGHT-80))

        # Display instructions
        inst_text = small_font.render("Touch START to run animation", True, WHITE)
        screen.blit(inst_text, (10, 80))

        pygame.display.flip()
        clock.tick(30)

    # Cleanup animation process
    if anim_proc and anim_proc.poll() is None:
        print("Terminating animation process...")
        anim_proc.terminate()
        try:
            anim_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            print("Force killing animation process...")
            anim_proc.kill()

    # Cleanup
    if pitft:
        del pitft
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


