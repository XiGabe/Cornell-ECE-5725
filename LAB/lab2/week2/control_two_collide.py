#!/usr/bin/env python3
"""
control_two_collide.py - Level 1/2 UI to control two_collide animation
Level 1: Start, Quit
Level 2: Pause/Restart, Faster, Slower, Back
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
YELLOW = (240, 200, 0)
BLUE = (0, 128, 255)

WIDTH, HEIGHT = 320, 240

def setup_env():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'dummy')
        os.putenv('SDL_MOUSEDEV', '/dev/null')
        os.putenv('DISPLAY', '')

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
    font = pygame.font.Font(None, 30)

    # Level 1 buttons
    start_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    quit_rect  = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)
    # Level 2 buttons
    pause_rect  = pygame.Rect(10, 10, 80, 34)
    faster_rect = pygame.Rect(100, 10, 80, 34)
    slower_rect = pygame.Rect(190, 10, 80, 34)
    back_rect   = pygame.Rect(WIDTH-70, HEIGHT-36, 60, 28)

    mode = 'menu1'  # 'menu1' or 'play'
    anim = TwoCollide()
    clock = pygame.time.Clock()
    bailout_deadline = time.time() + 120

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if mode == 'menu1':
                    if start_rect.collidepoint(x, y):
                        mode = 'play'
                    elif quit_rect.collidepoint(x, y):
                        running = False
                    else:
                        print(f"Touch at {x}, {y}")
                else:  # play mode (menu2)
                    if pause_rect.collidepoint(x, y):
                        anim.pause = not anim.pause
                    elif faster_rect.collidepoint(x, y):
                        anim.speed_scale = min(5.0, anim.speed_scale * 1.25)
                    elif slower_rect.collidepoint(x, y):
                        anim.speed_scale = max(0.2, anim.speed_scale / 1.25)
                    elif back_rect.collidepoint(x, y):
                        mode = 'menu1'
                    else:
                        print(f"Touch at {x}, {y}")

        if time.time() > bailout_deadline:
            running = False

        screen.fill(BLACK)
        if mode == 'menu1':
            pygame.draw.rect(screen, GREEN, start_rect)
            pygame.draw.rect(screen, RED,   quit_rect)
            screen.blit(font.render('START', True, WHITE), font.render('START', True, WHITE).get_rect(center=start_rect.center))
            screen.blit(font.render('QUIT',  True, WHITE), font.render('QUIT',  True, WHITE).get_rect(center=quit_rect.center))
        else:
            anim.update()
            anim.draw(screen)
            pygame.draw.rect(screen, YELLOW, pause_rect)
            pygame.draw.rect(screen, GREEN,  faster_rect)
            pygame.draw.rect(screen, BLUE,   slower_rect)
            pygame.draw.rect(screen, RED,    back_rect)
            screen.blit(font.render('PAUSE',  True, BLACK), font.render('PAUSE',  True, BLACK).get_rect(center=pause_rect.center))
            screen.blit(font.render('FASTER', True, BLACK), font.render('FASTER', True, BLACK).get_rect(center=faster_rect.center))
            screen.blit(font.render('SLOWER', True, BLACK), font.render('SLOWER', True, BLACK).get_rect(center=slower_rect.center))
            screen.blit(font.render('BACK',   True, WHITE), font.render('BACK',   True, WHITE).get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


