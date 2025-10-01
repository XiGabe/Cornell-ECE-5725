#!/usr/bin/env python3
"""
control_two_collide.py - Level 1/2 UI to control two_collide animation
Level 1: Start, Quit
Level 2: Pause/Restart, Faster, Slower, Back
Works on monitor and piTFT. Requires pigame.py & pitft_touchscreen.py for piTFT.
ECE 5725 Lab 2 Week 2
"""
import os
import sys
import time
import pygame
import RPi.GPIO as GPIO

USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (220, 0, 0)
YELLOW = (240, 200, 0)
BLUE = (0, 128, 255)
GRAY = (128, 128, 128)

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

class TwoCollide:
    def __init__(self):
        self.radius = 12
        self.balls = [
            {'x': WIDTH*0.35, 'y': HEIGHT*0.5, 'vx': 2.5, 'vy': 1.8, 'color': RED},
            {'x': WIDTH*0.65, 'y': HEIGHT*0.5, 'vx': -1.8, 'vy': -2.2, 'color': BLUE},
        ]
        self.pause = False
        self.speed_scale = 1.0

    def update(self):
        if self.pause:
            return
        r = self.radius
        for b in self.balls:
            b['x'] += b['vx'] * self.speed_scale
            b['y'] += b['vy'] * self.speed_scale
            if b['x'] - r < 0 or b['x'] + r > WIDTH:
                b['vx'] = -b['vx']
            if b['y'] - r < 0 or b['y'] + r > HEIGHT:
                b['vy'] = -b['vy']
        # collision
        dx = self.balls[1]['x'] - self.balls[0]['x']
        dy = self.balls[1]['y'] - self.balls[0]['y']
        if dx*dx + dy*dy <= (2*self.radius)*(2*self.radius):
            self.resolve_collision()

    def resolve_collision(self):
        import math
        b1, b2 = self.balls
        dx = b2['x'] - b1['x']
        dy = b2['y'] - b1['y']
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        nx, ny = dx/dist, dy/dist
        dvx = b1['vx'] - b2['vx']
        dvy = b1['vy'] - b2['vy']
        rel = dvx*nx + dvy*ny
        if rel > 0:
            return
        b1['vx'] -= rel*nx
        b1['vy'] -= rel*ny
        b2['vx'] += rel*nx
        b2['vy'] += rel*ny

    def draw(self, screen):
        for b in self.balls:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), self.radius)

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

    font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 24)

    # Level 1 buttons - positioned to avoid interference
    start_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    quit_rect  = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)

    # Level 2 buttons - positioned to not interfere with animation
    pause_rect  = pygame.Rect(10, 10, 70, 30)
    faster_rect = pygame.Rect(90, 10, 70, 30)
    slower_rect = pygame.Rect(170, 10, 70, 30)
    back_rect   = pygame.Rect(WIDTH-60, HEIGHT-35, 50, 25)

    mode = 'menu1'  # 'menu1' or 'play'
    anim = TwoCollide()
    clock = pygame.time.Clock()

    # Setup GPIO for physical bailout button
    gpio_available = setup_gpio()

    # Longer timeout for demonstration
    bailout_deadline = time.time() + 300  # 5 minutes

    # Touch display
    last_touch = None
    touch_display_time = 0

    print("Control Two Collide Started")
    print("Level 1: START (begin animation), QUIT (exit)")
    print("Level 2: PAUSE, FASTER, SLOWER, BACK (to menu)")
    print("Physical bailout: GPIO27 button")
    print("-" * 50)

    running = True
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

                if mode == 'menu1':
                    if start_rect.collidepoint(x, y):
                        mode = 'play'
                        print("Started animation - entering Level 2 controls")
                        # Reset animation state when starting
                        anim = TwoCollide()
                    elif quit_rect.collidepoint(x, y):
                        print("Quit button pressed - exiting")
                        running = False
                    else:
                        print(f"Touch at ({x}, {y}) - Level 1 menu")
                else:  # play mode (menu2)
                    if pause_rect.collidepoint(x, y):
                        anim.pause = not anim.pause
                        status = "paused" if anim.pause else "resumed"
                        print(f"Animation {status}")
                    elif faster_rect.collidepoint(x, y):
                        old_speed = anim.speed_scale
                        anim.speed_scale = min(5.0, anim.speed_scale * 1.25)
                        print(f"Speed: {old_speed:.2f}x -> {anim.speed_scale:.2f}x")
                    elif slower_rect.collidepoint(x, y):
                        old_speed = anim.speed_scale
                        anim.speed_scale = max(0.2, anim.speed_scale / 1.25)
                        print(f"Speed: {old_speed:.2f}x -> {anim.speed_scale:.2f}x")
                    elif back_rect.collidepoint(x, y):
                        mode = 'menu1'
                        print("Returned to Level 1 menu")
                    else:
                        print(f"Touch at ({x}, {y}) - Level 2 controls")

        # Check timeout
        if current_time > bailout_deadline:
            print("Timeout reached - exiting")
            running = False

        # Draw screen
        screen.fill(BLACK)

        if mode == 'menu1':
            # Level 1: Main menu
            # Title
            title_text = font.render("Two Collide Control", True, WHITE)
            title_rect = title_text.get_rect(centerx=WIDTH//2, y=20)
            screen.blit(title_text, title_rect)

            # Instructions
            inst_text = small_font.render("Touch START to begin animation", True, GRAY)
            inst_rect = inst_text.get_rect(centerx=WIDTH//2, y=HEIGHT//2)
            screen.blit(inst_text, inst_rect)

            # Buttons
            pygame.draw.rect(screen, GREEN, start_rect)
            pygame.draw.rect(screen, RED,   quit_rect)

            screen.blit(font.render('START', True, WHITE), font.render('START', True, WHITE).get_rect(center=start_rect.center))
            screen.blit(font.render('QUIT',  True, WHITE), font.render('QUIT',  True, WHITE).get_rect(center=quit_rect.center))
        else:
            # Level 2: Animation controls
            # Update and draw animation
            anim.update()
            anim.draw(screen)

            # Control panel background (semi-transparent overlay)
            panel_surface = pygame.Surface((WIDTH, 50))
            panel_surface.set_alpha(200)
            panel_surface.fill(BLACK)
            screen.blit(panel_surface, (0, 0))

            # Level 2 buttons
            pause_color = RED if anim.pause else YELLOW
            pygame.draw.rect(screen, pause_color, pause_rect)
            pygame.draw.rect(screen, GREEN,  faster_rect)
            pygame.draw.rect(screen, BLUE,   slower_rect)
            pygame.draw.rect(screen, RED,    back_rect)

            # Button labels
            pause_text = 'RESUME' if anim.pause else 'PAUSE'
            screen.blit(font.render(pause_text,  True, BLACK), font.render(pause_text,  True, BLACK).get_rect(center=pause_rect.center))
            screen.blit(font.render('FASTER', True, BLACK), font.render('FASTER', True, BLACK).get_rect(center=faster_rect.center))
            screen.blit(font.render('SLOWER', True, BLACK), font.render('SLOWER', True, BLACK).get_rect(center=slower_rect.center))
            screen.blit(font.render('BACK',   True, WHITE), font.render('BACK',   True, WHITE).get_rect(center=back_rect.center))

            # Speed indicator
            speed_text = small_font.render(f"Speed: {anim.speed_scale:.2f}x", True, WHITE)
            screen.blit(speed_text, (WIDTH-80, 75))

            # Pause indicator
            if anim.pause:
                pause_indicator = font.render("PAUSED", True, RED)
                pause_rect = pause_indicator.get_rect(centerx=WIDTH//2, y=HEIGHT//2)
                screen.blit(pause_indicator, pause_rect)

        # Display last touch coordinates
        if last_touch:
            touch_text = small_font.render(f"Touch: ({last_touch[0]}, {last_touch[1]})", True, BLUE)
            screen.blit(touch_text, (10, HEIGHT-25))

        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    if pitft:
        del pitft
    if gpio_available:
        GPIO.cleanup()

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


