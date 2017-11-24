#!/usr/bin/python
import math, random, time
import pygame_sdl2 as pygame
from pygame_sdl2.locals import *

SCREEN_SIZE = [1024, 768]
FRAME_PER_SECOND = 30
MS_PER_FRAME = 1000.0 / FRAME_PER_SECOND

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF)
    box_color = (255, 255, 255)
    mid_x = SCREEN_SIZE[0] / 2
    mid_y = SCREEN_SIZE[1] / 2
    while True:
        delta_t = clock.tick(FRAME_PER_SECOND)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == KEYDOWN:
                # Exit when user presses ESC or Q.
                if e.key in (27, 113):
                    return
        screen.fill((0, 0, 0))
        bs = 100
        pygame.draw.rect(screen, box_color, (mid_x-bs/2, mid_y-bs/2, bs, bs), 1)
        pygame.display.flip()


if __name__ == '__main__':
    main()

