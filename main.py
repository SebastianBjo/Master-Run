import pygame
import sys
import random
import math
import time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Combat Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 100, 255)
GREEN = (0, 255, 0)

# Clock
FPS = 60
clock = pygame.time.Clock()


# --- Player Class ---
class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.size = 30
        self.color = BLUE
        self.speed = 4
        self.dash_speed = 12
        self.last_dash = 0
        self.dash_cooldown = 2  # seconds
        self.last_shot = 0
        self.shot_cooldown = 0.3  # seconds
        self.projectiles = []

    def handle_movement(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed
        self.x += dx
        self.y += dy

        # Boundaries
        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def dash(self, keys):
        if keys[pygame.K_e] and time.time() - self.last_dash > self.dash_cooldown:
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy = -self.dash_speed
            if keys[pygame.K_s]:
                dy = self.dash_speed
            if keys[pygame.K_a]:
                dx = -self.dash_speed
            if keys[pygame.K_d]:
                dx = self.dash_speed
            self.x += dx * 5
            self.y += dy * 5
            self.last_dash = time.time()

    def shoot(self, mouse_buttons, mouse_pos):
        if mouse_buttons[0] and time.time() - self.last_shot > self.shot_cooldown:
            mx, my = mouse_pos
            angle = math.atan2(my - (self.y + self.size // 2), mx - (self.x + self.size // 2))
            velx = math.cos(angle) * 8
            vely = math.sin(angle) * 8
            self.projectiles.append(Projectile(self.x + self.size//2, self.y + self.size//2, velx, vely))
            self.last_shot = time.time()

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))
        for proj in self.projectiles:
            proj.draw(win)


# --- Projectile Class ---
class Projectile:
    def __init__(self, x, y, velx, vely):
        self.x, self.y = x, y
        self.velx, self.vely = velx, vely
        self.radius = 5
        self.color = GREEN

    def update(self):
        self.x += self.velx
        self.y += self.vely

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)


# --- Enemy Class ---
class Enemy:
    def __init__(self):
        self.x = random.choice([0, WIDTH])
        self.y = random.randint(0, HEIGHT)
        self.size = 25
        self.color = RED
        self.speed = 2

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))


# --- Main Game Loop ---
def main():
    player = Player()
    enemies = [Enemy() for _ in range(5)]

    running = True
    while running:
        clock.tick(FPS)
        WIN.fill(BLACK)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Inputs
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        player.handle_movement(keys)
        player.dash(keys)
        player.shoot(mouse_buttons, mouse_pos)

        # Update projectiles
        for proj in player.projectiles[:]:
            proj.update()
            if proj.off_screen():
                player.projectiles.remove(proj)

        # Update enemies
        for enemy in enemies[:]:
            enemy.update(player)
            for proj in player.projectiles[:]:
                if (enemy.x < proj.x < enemy.x + enemy.size and
                        enemy.y < proj.y < enemy.y + enemy.size):
                    enemies.remove(enemy)
                    player.projectiles.remove(proj)
                    enemies.append(Enemy())
                    break

        # Draw
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import pygame
import sys
import random
import math
import time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Combat Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 50, 50)
BLUE  = (50, 120, 255)
GREEN = (0, 255, 0)
GREY  = (100, 100, 100)

# Clock
FPS = 60
clock = pygame.time.Clock()


# --- Player Class ---
class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.radius = 20
        self.speed = 4
        self.dash_speed = 12
        self.last_dash = 0
        self.dash_cooldown = 2  # seconds
        self.last_shot = 0
        self.shot_cooldown = 0.3  # seconds
        self.projectiles = []

        # Health
        self.max_health = 100
        self.health = self.max_health

    def handle_movement(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed
        self.x += dx
        self.y += dy

        # Boundaries
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def dash(self, keys):
        if keys[pygame.K_e] and time.time() - self.last_dash > self.dash_cooldown:
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy = -self.dash_speed
            if keys[pygame.K_s]:
                dy = self.dash_speed
            if keys[pygame.K_a]:
                dx = -self.dash_speed
            if keys[pygame.K_d]:
                dx = self.dash_speed
            self.x += dx * 5
            self.y += dy * 5
            self.last_dash = time.time()

    def shoot(self, mouse_buttons, mouse_pos):
        if mouse_buttons[0] and ti_
