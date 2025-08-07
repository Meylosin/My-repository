import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')  # allow headless

import pygame
import random
import sys

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 416, 416  # 13x13 grid (32 px tiles) like Battle City
TILE_SIZE = 32
FPS = 60

# Directions
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
DIR_VECTORS = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 8

    def update(self, obstacles):
        dx, dy = DIR_VECTORS[self.direction]
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
                any(self.rect.colliderect(ob.rect) for ob in obstacles)):
            self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = UP
        self.speed = 2
        self.cooldown = 0

    def move(self, direction, obstacles):
        dx, dy = DIR_VECTORS[direction]
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)
        if not any(new_rect.colliderect(ob.rect) for ob in obstacles):
            self.rect = new_rect
            self.direction = direction

    def shoot(self, bullets):
        if self.cooldown == 0:
            bx = self.rect.centerx
            by = self.rect.centery
            bullet = Bullet(bx, by, self.direction)
            bullets.add(bullet)
            self.cooldown = FPS // 2

    def update(self):
        if self.cooldown:
            self.cooldown -= 1

class Enemy(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 0, 0))
        self.move_timer = 0

    def update(self, obstacles, bullets):
        super().update()
        if self.move_timer == 0:
            self.move(random.choice([UP, DOWN, LEFT, RIGHT]), obstacles)
            if random.random() < 0.02:
                self.shoot(bullets)
            self.move_timer = FPS // 4
        else:
            self.move_timer -= 1

def create_level():
    obstacles = pygame.sprite.Group()
    layout = [
        "#############",
        "#...........#",
        "#.###.###.#.#",
        "#...........#",
        "#.###.#.###.#",
        "#...........#",
        "#.###.###.#.#",
        "#...........#",
        "#.#.###.###.#",
        "#...........#",
        "#.###.#.###.#",
        "#...........#",
        "#############",
    ]
    for y, row in enumerate(layout):
        for x, ch in enumerate(row):
            if ch == '#':
                block = pygame.sprite.Sprite()
                block.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                block.image.fill((150, 75, 0))
                block.rect = block.image.get_rect(topleft=(x*TILE_SIZE, y*TILE_SIZE))
                obstacles.add(block)
    return obstacles

def run_game(max_frames=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    player = Tank(6*TILE_SIZE, 12*TILE_SIZE, (0, 255, 0))
    enemy = Enemy(6*TILE_SIZE, TILE_SIZE)
    tanks = pygame.sprite.Group(player, enemy)
    bullets = pygame.sprite.Group()
    obstacles = create_level()

    frames = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot(bullets)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(UP, obstacles)
        elif keys[pygame.K_DOWN]:
            player.move(DOWN, obstacles)
        elif keys[pygame.K_LEFT]:
            player.move(LEFT, obstacles)
        elif keys[pygame.K_RIGHT]:
            player.move(RIGHT, obstacles)

        bullets.update(obstacles)
        player.update()
        enemy.update(obstacles, bullets)

        for bullet in bullets.copy():
            if bullet.rect.colliderect(enemy.rect):
                enemy.kill()
                bullet.kill()

        screen.fill((0, 0, 0))
        obstacles.draw(screen)
        tanks.draw(screen)
        bullets.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

        frames += 1
        if max_frames and frames >= max_frames:
            running = False

    pygame.quit()

if __name__ == '__main__':
    frames = None
    if len(sys.argv) > 1 and sys.argv[1].startswith('--frames='):
        frames = int(sys.argv[1].split('=')[1])
    run_game(frames)
