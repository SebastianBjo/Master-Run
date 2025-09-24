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
        if mouse_buttons[0] and time.time() - self.last_shot > self.shot_cooldown:
            mx, my = mouse_pos
            angle = math.atan2(my - self.y, mx - self.x)
            velx = math.cos(angle) * 8
            vely = math.sin(angle) * 8
            self.projectiles.append(Projectile(self.x, self.y, velx, vely))
            self.last_shot = time.time()

    def draw(self, win):
        pygame.draw.circle(win, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(win, WHITE, (int(self.x), int(self.y)), self.radius, 2)

        # Draw health bar
        bar_width, bar_height = 150, 15
        x, y = 20, 20
        pygame.draw.rect(win, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(win, GREEN, (x, y, bar_width * (self.health / self.max_health), bar_height))

        # Projectiles
        for proj in self.projectiles:
            proj.draw(win)


# --- Projectile Class ---
class Projectile:
    def __init__(self, x, y, velx, vely):
        self.x, self.y = x, y
        self.velx, self.vely = velx, vely
        self.radius = 5
        self.color = GREEN
        self.damage = 5  # smaller so health bar is visible

    def update(self):
        self.x += self.velx
        self.y += self.vely

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)


# --- Enemy Class ---
class Enemy:
    def __init__(self, wave):
        self.x = random.choice([0, WIDTH])
        self.y = random.randint(0, HEIGHT)
        self.radius = 20
        self.speed = 1.5 + (wave * 0.2)
        self.max_health = 30 + (wave * 5)
        self.health = self.max_health

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Collide with player
        if math.hypot(player.x - self.x, player.y - self.y) < self.radius + player.radius:
            player.health -= 0.3  # damage on touch

    def draw(self, win):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), self.radius)
        # Horns
        pygame.draw.polygon(win, RED, [(self.x - 10, self.y - 20), (self.x - 5, self.y - 5), (self.x, self.y - 20)])
        pygame.draw.polygon(win, RED, [(self.x + 10, self.y - 20), (self.x + 5, self.y - 5), (self.x, self.y - 20)])
        # Health bar
        bar_width = self.radius * 2
        pygame.draw.rect(win, RED, (self.x - self.radius, self.y - self.radius - 10, bar_width, 5))
        pygame.draw.rect(win, GREEN, (self.x - self.radius, self.y - self.radius - 10, bar_width * (self.health / self.max_health), 5))


# --- Main Game Loop ---
def main():
    player = Player()
    wave = 1
    enemies = [Enemy(wave) for _ in range(5)]

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
                if math.hypot(enemy.x - proj.x, enemy.y - proj.y) < enemy.radius + proj.radius:
                    enemy.health -= proj.damage
                    if proj in player.projectiles:
                        player.projectiles.remove(proj)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        break

        # New wave
        if not enemies:
            wave += 1
            enemies = [Enemy(wave) for _ in range(5 + wave)]

        # Draw
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        # Wave counter
        font = pygame.font.SysFont(None, 36)
        wave_text = font.render(f"Wave: {wave}", True, WHITE)
        WIN.blit(wave_text, (WIDTH - 150, 20))

        # Game over
        if player.health <= 0:
            over_text = font.render("GAME OVER", True, RED)
            WIN.blit(over_text, (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)
            running = False

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
