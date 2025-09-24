#!/usr/bin/env python3
"""
two_collide.py - Two balls with elastic collision response in 2D
"""
import os
import sys
import time
import math
import pygame

USE_TFT = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)

WIDTH, HEIGHT = 320, 240

def init_display():
    if USE_TFT:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    return screen

def resolve_elastic_collision(b1, b2, radius):
    # Based on equal-mass elastic collision in 2D
    dx = b2['x'] - b1['x']
    dy = b2['y'] - b1['y']
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    nx, ny = dx/dist, dy/dist
    # relative velocity
    dvx = b1['vx'] - b2['vx']
    dvy = b1['vy'] - b2['vy']
    rel = dvx*nx + dvy*ny
    if rel > 0:
        return
    # exchange normal components (equal masses)
    b1['vx'] -= rel*nx
    b1['vy'] -= rel*ny
    b2['vx'] += rel*nx
    b2['vy'] += rel*ny
    # positional correction to avoid sticking
    overlap = 2*radius - dist
    if overlap > 0:
        b1['x'] -= nx * overlap/2
        b1['y'] -= ny * overlap/2
        b2['x'] += nx * overlap/2
        b2['y'] += ny * overlap/2

def main():
    screen = init_display()
    clock = pygame.time.Clock()
    radius = 12
    balls = [
        {'x': WIDTH*0.35, 'y': HEIGHT*0.5, 'vx': 2.5, 'vy': 1.8, 'color': RED},
        {'x': WIDTH*0.65, 'y': HEIGHT*0.5, 'vx': -1.8, 'vy': -2.2, 'color': BLUE},
    ]

    bailout_deadline = time.time() + 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if time.time() > bailout_deadline:
            running = False

        for b in balls:
            b['x'] += b['vx']
            b['y'] += b['vy']
            if b['x'] - radius < 0 or b['x'] + radius > WIDTH:
                b['vx'] = -b['vx']
            if b['y'] - radius < 0 or b['y'] + radius > HEIGHT:
                b['vy'] = -b['vy']

        # collision check
        dx = balls[1]['x'] - balls[0]['x']
        dy = balls[1]['y'] - balls[0]['y']
        if dx*dx + dy*dy <= (2*radius)*(2*radius):
            resolve_elastic_collision(balls[0], balls[1], radius)

        screen.fill(BLACK)
        for b in balls:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), radius)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()


