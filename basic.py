#!/usr/bin/python
import math
import pygame
from pygame.locals import *

FRAME_PER_SECOND = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
img = pygame.image.load('pack.png')
i = 0
while True:
    delta_t = clock.tick(FRAME_PER_SECOND)
    print delta_t
    i = (i + 1) % 360
    rotated = pygame.transform.rotate(img, i * math.pi / 180)
    screen.fill((0, 0, 0))
    # screen.blit(rotated, (50, 100))
    screen.blit(img, (50 + i, 100))
    pygame.display.flip()
