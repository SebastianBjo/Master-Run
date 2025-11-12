import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Combat Game")

# Colors
WHITE = (255, 255, 255)
PLAYER_COLOR = (50, 205, 50)  # Green
ENEMY_COLOR = (255, 0, 0)     # Red
BULLET_COLOR = (255, 255, 0)  # Yellow

# Player settings
PLAYER_SIZE = 20
PLAYER_SPEED = 3

# Dash settings
DASH_COOLDOWN = 1000  # milliseconds
DASH_DISTANCE = 100

# Shooting settings
SHOOT_COOLDOWN = 500  # milliseconds
BULLET_SPEED = 7

# Enemy settings
ENEMY_SIZE = 20
ENEMY_SPEED = 2
ENEMY_SPAWN_TIME = 2000  # milliseconds

# Setup clock
clock = pygame.time.Clock()

# Font for text
font = pygame.font.SysFont(None, 24)

# Helper functions
def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.last_dash_time = 0
        self.last_shot_time = 0
        self.dash_cooldown = DASH_COOLDOWN
        self.shoot_cooldown = SHOOT_COOLDOWN
        self.dashing = False
        self.dash_direction = pygame.Vector2(0,0)
        self.upgrades = {
            'fire_rate': 1,  # multiplier
            'damage': 1,
            'multi_shot': False,  # for future upgrades
        }

    def move(self, keys_pressed):
        dir_x, dir_y = 0, 0
        if keys_pressed[pygame.K_w]:
            dir_y = -1
        if keys_pressed[pygame.K_s]:
            dir_y = 1
        if keys_pressed[pygame.K_a]:
            dir_x = -1
        if keys_pressed[pygame.K_d]:
            dir_x = 1
        dir_vector = pygame.Vector2(dir_x, dir_y)
        if dir_vector.length() != 0:
            dir_vector = dir_vector.normalize()
            self.rect.x += dir_vector.x * self.speed
            self.rect.y += dir_vector.y * self.speed

    def dash(self, keys_pressed):
        now = pygame.time.get_ticks()
        if now - self.last_dash_time >= self.dash_cooldown:
            dir_x, dir_y = 0,0
            if keys_pressed[pygame.K_w]:
                dir_y = -1
            if keys_pressed[pygame.K_s]:
                dir_y = 1
            if keys_pressed[pygame.K_a]:
                dir_x = -1
            if keys_pressed[pygame.K_d]:
                dir_x = 1
            direction = pygame.Vector2(dir_x, dir_y)
            if direction.length() != 0:
                direction = direction.normalize()
                self.rect.x += direction.x * DASH_DISTANCE
                self.rect.y += direction.y * DASH_DISTANCE
                self.last_dash_time = now

    def shoot(self, mouse_pos, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            # Calculate direction
            direction = pygame.Vector2(mouse_pos) - pygame.Vector2(self.rect.center)
            if direction.length() != 0:
                direction = direction.normalize()
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, direction))
                self.last_shot_time = now

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

# Bullet class
class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.direction = direction
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self):
        pygame.draw.rect(screen, BULLET_COLOR, self.rect)

# Enemy class
class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(0, WIDTH - ENEMY_SIZE),
            random.randint(0, HEIGHT - ENEMY_SIZE),
            ENEMY_SIZE,
            ENEMY_SIZE
        )
        self.speed = ENEMY_SPEED

    def update(self, player_pos):
        direction = pygame.Vector2(player_pos) - pygame.Vector2(self.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()
            self.rect.x += direction.x * self.speed
            self.rect.y += direction.y * self.speed

    def draw(self):
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect)

# Main game function
def main():
    player = Player()
    bullets = []
    enemies = []

    last_enemy_spawn = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(60)
        screen.fill((0,0,0))
        now = pygame.time.get_ticks()

        # Spawn enemies
        if now - last_enemy_spawn >= ENEMY_SPAWN_TIME:
            enemies.append(Enemy())
            last_enemy_spawn = now

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

        keys_pressed = pygame.key.get_pressed()

        # Movement
        player.move(keys_pressed)

        # Dash
        if keys_pressed[pygame.K_e]:
            player.dash(keys_pressed)

        # Shooting
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            player.shoot(mouse_pos, bullets)

        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            # Remove if off-screen
            if (bullet.rect.x < 0 or bullet.rect.x > WIDTH or
                bullet.rect.y < 0 or bullet.rect.y > HEIGHT):
                bullets.remove(bullet)

        # Update enemies
        for enemy in enemies[:]:
            enemy.update(player.rect.center)

        # Check for collisions
        for enemy in enemies[:]:
            if enemy.rect.colliderect(player.rect):
                # For now, just remove enemy on collision
                enemies.remove(enemy)
                # Could implement health, game over, etc.

            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):
                    enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    # Can add upgrade logic here
                    break

        # Draw everything
        player.draw()
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()

        # Draw UI
        draw_text("Press WASD to move, E to dash, Left Click to shoot", 10, 10)
        draw_text("Enemies: {}".format(len(enemies)), 10, 30)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
