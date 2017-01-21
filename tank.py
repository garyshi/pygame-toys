#!/usr/bin/python
import math, random
import pygame
from pygame.locals import *


def get_speed_vector(pos, dest, speed):
    # TODO: migrate to pygame.math.Vector2 when it's ready.
    v_x = dest[0] - pos[0]
    v_y = dest[1] - pos[1]
    v_length = math.sqrt(v_x * v_x + v_y * v_y)
    if v_length < 1: return None
    # Slow down when it's close.
    speed = min(speed, v_length)
    return (v_x / v_length * speed, v_y / v_length * speed)


class Bullet(object):
    def __init__(self, pos, init_dest, bounds):
        self.c = 3
        self.bounds = bounds
        (self.x, self.y) = pos
        self.vector = get_speed_vector(pos, init_dest, 10)
        self.surface = pygame.Surface((2 * self.c, 2 * self.c))
        pygame.draw.circle(self.surface, (255, 255, 255), (self.c, self.c), self.c-1)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def step(self, delta_t, enemies, friends):
        for i in (0.2, 0.4, 0.6, 0.8, 1):
            cx = self.x + i * self.vector[0]
            cy = self.y + i * self.vector[1]
            for e in enemies:
                if e and e.health > 0:
                    if abs(cx - e.x) < 8 and abs(cy - e.y) < 8:
                        e.health -= 1
                        if e.health <= 0: e.die()
                        return False
        self.x = round(self.x + self.vector[0])
        self.y = round(self.y + self.vector[1])
        return (self.bounds[0] < self.x < self.bounds[2] and
                self.bounds[1] < self.y < self.bounds[3])

class Tank(object):
    def __init__(self, bounds, pos, color, health, speed_ratio=0.3):
        self.c = 10  # center, half of the sprite size.
        self.color = color
        self.health = health
        self.speed_ratio = speed_ratio  # ratio of the delta_t, in milliseconds.
        self.bounds = bounds
        (self.x, self.y) = pos
        self.dest = pos
        self.surface = pygame.Surface((2 * self.c, 2 * self.c))
        pygame.draw.circle(self.surface, self.color, (self.c, self.c), self.c-1)
        self.num_bullets = 3
        self.bullets = [None] * self.num_bullets

    def die(self):
        self.surface.fill((0, 0, 0))
        pygame.draw.circle(self.surface, self.color, (self.c, self.c), self.c-1, 2)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def draw_bullets(self, screen):
        if self.health > 0:
            for bullet in self.bullets:
                if bullet: bullet.draw(screen)

    def set_dest(self, pos):
        d_x = pos[0] - self.c
        d_y = pos[1] - self.c
        d_x_min = self.bounds[0]
        d_x_max = self.bounds[2]
        d_y_min = self.bounds[1]
        d_y_max = self.bounds[3]
        if d_x < d_x_min: d_x = d_x_min
        elif d_x > d_x_max: d_x = d_x_max
        if d_y < d_y_min: d_y = d_y_min
        elif d_y > d_y_max: d_y = d_y_max
        self.dest = (d_x, d_y)

    def shoot(self, dest):
        for i in xrange(self.num_bullets):
            if not self.bullets[i]:
                self.bullets[i] = Bullet((self.x, self.y), dest, self.bounds)
                break

    def step(self, delta_t, enemies, friends):
        speed_v = get_speed_vector((self.x, self.y), self.dest, self.speed_ratio * delta_t)
        if speed_v:
            self.x += round(speed_v[0])
            self.y += round(speed_v[1])
        for i, bullet in enumerate(self.bullets):
            if bullet:
                if not bullet.step(delta_t, enemies, friends):
                    self.bullets[i] = None


class AITank(Tank):
    def __init__(self, *args, **kwargs):
        super(AITank, self).__init__(*args, **kwargs)
        self.step_counter = 0

    def ai_step(self, enemies, friends):
        if self.health <= 0: return
        self.step_counter += 1
        r = random.random()
        if self.step_counter == 1 or r < 0.1:
            move_range = 80
            bounds = [max(self.bounds[0], self.x - move_range),
                      max(self.bounds[1], self.y - move_range),
                      min(self.bounds[2], self.x + move_range),
                      min(self.bounds[3], self.y + move_range)]
            self.set_dest((random.randint(bounds[0], bounds[2]),
                           random.randint(bounds[1], bounds[3])))
            if r < 0.005:
                e = random.choice(enemies)
                if e.health > 0:
                    self.shoot((e.x+e.c, e.y+e.c))


def populate_aitanks(num_enemies, player, bounds, min_dist):
    result = []
    for i in range(num_enemies):
        x = random.randint(bounds[0], bounds[2])
        y = random.randint(bounds[1], bounds[3])
        start_over = False
        if abs(x - player.x) < min_dist and abs(y - player.y) < min_dist:
            start_over = True
        for s in result:
            if abs(x - s.x) < min_dist and abs(y - s.y) < min_dist:
                start_over = True
                break
        if start_over: continue
        result.append(AITank(bounds=bounds,
                             pos=(x, y),
                             color=(255, 128, 128),
                             health=1, speed_ratio=0.2))
    return result


def main():
    FRAME_PER_SECOND = 60
    clock = pygame.time.Clock()
    screen_w = 1024
    screen_h = 768
    screen = pygame.display.set_mode((screen_w, screen_h), DOUBLEBUF)
    player = Tank(bounds=(0, 0, screen_w, screen_h),
                  pos=(screen_w/2, screen_h/2),
                  color=(128, 128, 255),
                  health=3)
    ai_tanks = populate_aitanks(5, player, (0, 0, screen_w, screen_h), 20)
    all_tanks = ai_tanks + [player]

    paused = False
    while True:
        delta_t = clock.tick(FRAME_PER_SECOND)
        for e in pygame.event.get():
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    player.set_dest(e.pos)
                elif e.button == 3:
                    player.shoot(e.pos)
            elif e.type == KEYDOWN:
                if e.key == 113: return
                elif e.key == 32:
                    paused = not paused
        if not paused:
            for tank in ai_tanks:
                tank.ai_step([player], ai_tanks)
            player.step(delta_t, ai_tanks, [])
            for tank in ai_tanks:
                tank.step(delta_t, [player], ai_tanks)
            if player.health <= 0: break
        screen.fill((0, 0, 0))
        for tank in all_tanks: tank.draw(screen)
        for tank in all_tanks: tank.draw_bullets(screen)
        pygame.display.flip()

    while True:
        delta_t = clock.tick(FRAME_PER_SECOND)
        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key in (113,):
                return
        screen.fill((0, 0, 0))
        for tank in all_tanks: tank.draw(screen)
        for tank in all_tanks: tank.draw_bullets(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
