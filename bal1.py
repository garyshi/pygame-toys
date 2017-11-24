#!/usr/bin/python
import math, random, time
import pygame_sdl2 as pygame
from pygame_sdl2.locals import *

SCREEN_SIZE = [1024, 1024]
FRAME_PER_SECOND = 60
MS_PER_FRAME = 1000.0 / FRAME_PER_SECOND

G = 9.8
PI = math.pi
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ACTION_FORCE = 2.0

class StickOnBar(object):

    def __init__(self, angle=0.0, ang_v=0.0):
        self.mass = 1.0
        self.bar_len = 10.0
        self.stick_len = 2.0
        # This is not in use. Don't know how to make it work in ang_accel_* below..
        self.mass_pos = 0.5  # 0 is on the bar, 1 is at the head.
        self.stick_pos = self.bar_len / 2
        self.angle = angle  # in radius. <0 when the head is at left, >0 when right.
        self.ang_v = ang_v  # radius/s. <0 when anti-clockwise, >0 when clockwise.

    def Step(self, delta_t, action):
        if self.stick_pos <= 0 and action < 0: action = 0
        if self.stick_pos >= self.bar_len and action > 0: action = 0
        dts = delta_t / 1000.0
        self.angle += self.ang_v * dts
        ang_accel_head = math.sin(self.angle) * G  # this *mass is the force, and /mass is the accel
        ang_accel_tail = (action * ACTION_FORCE * math.cos(self.angle)) / self.mass
        self.ang_v += (ang_accel_head - ang_accel_tail) * dts
        self.ang_v *= 0.999  # friction
        self.stick_pos += action * 0.02

    def Render(self, surface):
        margin = 10
        s_width = surface.get_width() - margin*2
        s_height = surface.get_height() - margin*2
        scale = min(s_width, s_height) / self.bar_len
        bar_y = margin + s_height * 0.5
        pygame.draw.line(surface, BLACK, (margin, bar_y), (s_width, bar_y))
        stick_head_x = margin + (self.stick_pos + math.sin(self.angle) * self.stick_len) * scale
        stick_head_y = bar_y - math.cos(self.angle) * self.stick_len * scale
        pygame.draw.line(surface, BLACK, (margin+self.stick_pos*scale, bar_y), (stick_head_x, stick_head_y))
        pygame.draw.circle(surface, BLACK, (stick_head_x, stick_head_y), 5)


def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF)
    sob = StickOnBar(ang_v=0.1)
    action = 0
    while True:
        delta_t = clock.tick(FRAME_PER_SECOND)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == KEYDOWN:
                # Exit when user presses ESC or Q.
                if e.key in (27, 113):
                    return
                if e.key == pygame.K_LEFT:
                    action = -1
                elif e.key == pygame.K_RIGHT:
                    action = 1
            elif e.type == KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                    action = 0
        sob.Step(delta_t, action)
        screen.fill(WHITE)
        sob.Render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()

