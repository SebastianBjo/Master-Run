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
YELLOW = (255, 255, 0)

# Clock
FPS = 60
clock = pygame.time.Clock()

# --- Buff Class ---
class Buff:
    def __init__(self, name, value, duration):
        self.name = name
        self.value = value
        self.end_time = time.time() + duration

# --- Player Class ---
class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.radius = 20
        self.speed = 4
        self.dash_speed = 12
        self.last_dash = 0
        self.dash_cooldown = 2
        self.last_shot = 0
        self.shot_cooldown = 0.3
        self.projectiles = []

        self.max_health = 100
        self.health = self.max_health

        # XP / Cash / Level
        self.xp = 0
        self.cash = 0
        self.level = 1

        # Upgradeable stats
        self.sp = 1
        self.splash = 0
        self.damage = 5

        # Active buffs
        self.buffs = []

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
            self.x += dx * self.sp
            self.y += dy * self.sp
            self.last_dash = time.time()

    def shoot(self, mouse_buttons, mouse_pos):
        if mouse_buttons[0] and time.time() - self.last_shot > self.shot_cooldown:
            mx, my = mouse_pos
            angle = math.atan2(my - self.y, mx - self.x)
            velx = math.cos(angle) * 8
            vely = math.sin(angle) * 8
            self.projectiles.append(Projectile(self.x, self.y, velx, vely, self.damage, self.splash))
            self.last_shot = time.time()

    def apply_buffs(self):
        for buff in self.buffs[:]:
            if time.time() > buff.end_time:
                if buff.name == "damage":
                    self.damage -= buff.value
                elif buff.name == "speed":
                    self.speed -= buff.value
                elif buff.name == "firerate":
                    self.shot_cooldown += buff.value
                elif buff.name == "sp":
                    self.sp -= buff.value
                self.buffs.remove(buff)

    def add_buff(self, buff):
        self.buffs.append(buff)
        if buff.name == "damage":
            self.damage += buff.value
        elif buff.name == "speed":
            self.speed += buff.value
        elif buff.name == "firerate":
            self.shot_cooldown = max(0.05, self.shot_cooldown - buff.value)
        elif buff.name == "sp":
            self.sp += buff.value

    def upgrade(self, stat):
        cost = 10 * self.level
        if self.cash >= cost:
            self.cash -= cost
            self.level += 1
            if stat == "speed":
                self.speed += 1
            elif stat == "damage":
                self.damage += 2
            elif stat == "firerate":
                self.shot_cooldown = max(0.05, self.shot_cooldown - 0.05)
            elif stat == "sp":
                self.sp += 1
            elif stat == "splash":
                self.splash += 1

    def draw(self, win):
        pygame.draw.circle(win, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(win, WHITE, (int(self.x), int(self.y)), self.radius, 2)

        # Health bar
        bar_width, bar_height = 150, 15
        pygame.draw.rect(win, RED, (20, 20, bar_width, bar_height))
        pygame.draw.rect(win, GREEN, (20, 20, bar_width * (self.health / self.max_health), bar_height))

        # XP / Cash
        font = pygame.font.SysFont(None, 28)
        xp_text = font.render(f"XP: {self.xp}", True, WHITE)
        cash_text = font.render(f"Cash: {self.cash}", True, WHITE)
        WIN.blit(xp_text, (20, 40))
        WIN.blit(cash_text, (20, 65))

        # Projectiles
        for proj in self.projectiles:
            proj.draw(win)


# --- Projectile Class ---
class Projectile:
    def __init__(self, x, y, velx, vely, damage, splash):
        self.x, self.y = x, y
        self.velx, self.vely = velx, vely
        self.radius = 5
        self.color = GREEN
        self.damage = damage
        self.splash = splash

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
            player.health -= 0.3

    def draw(self, win):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), self.radius)
        # Horns
        pygame.draw.polygon(win, RED, [(self.x - 10, self.y - 20), (self.x - 5, self.y - 5), (self.x, self.y - 20)])
        pygame.draw.polygon(win, RED, [(self.x + 10, self.y - 20), (self.x + 5, self.y - 5), (self.x, self.y - 20)])
        # Health bar
        bar_width = self.radius * 2
        pygame.draw.rect(win, RED, (self.x - self.radius, self.y - self.radius - 10, bar_width, 5))
        pygame.draw.rect(win, GREEN, (self.x - self.radius, self.y - self.radius - 10, bar_width * (self.health / self.max_health), 5))


# --- Shop Function ---
def open_shop(player):
    shop_open = True
    font = pygame.font.SysFont(None, 32)
    while shop_open:
        WIN.fill(BLACK)
        shop_items = [
            f"1. Speed (+1) - Cost: {10 * player.level}",
            f"2. Damage (+2) - Cost: {10 * player.level}",
            f"3. Fire Rate (-0.05s) - Cost: {10 * player.level}",
            f"4. SP (+1 dash) - Cost: {10 * player.level}",
            f"5. Splash (+1) - Cost: {10 * player.level}",
            "ESC. Exit shop"
        ]
        cash_text = font.render(f"Cash: {player.cash}", True, WHITE)
        WIN.blit(cash_text, (20, 20))
        for i, item in enumerate(shop_items):
            text = font.render(item, True, WHITE)
            WIN.blit(text, (20, 60 + i*30))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    shop_open = False
                elif event.key == pygame.K_1:
                    player.upgrade("speed")
                elif event.key == pygame.K_2:
                    player.upgrade("damage")
                elif event.key == pygame.K_3:
                    player.upgrade("firerate")
                elif event.key == pygame.K_4:
                    player.upgrade("sp")
                elif event.key == pygame.K_5:
                    player.upgrade("splash")


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

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if keys[pygame.K_u]:
            open_shop(player)

        player.handle_movement(keys)
        player.dash(keys)
        player.shoot(mouse_buttons, mouse_pos)
        player.apply_buffs()

        # Update projectiles
        for proj in player.projectiles[:]:
            proj.update()
            if proj.off_screen():
                player.projectiles.remove(proj)

        # Update enemies
        for enemy in enemies[:]:
            enemy.update(player)
            for proj in player.projectiles[:]:
                dist = math.hypot(enemy.x - proj.x, enemy.y - proj.y)
                if dist < enemy.radius + proj.radius:
                    enemy.health -= proj.damage
                    if proj.splash > 0:
                        # Splash damage to nearby enemies
                        for other in enemies:
                            if other != enemy and math.hypot(other.x - proj.x, other.y - proj.y) < proj.splash*20:
                                other.health -= proj.damage // 2
                    if proj in player.projectiles:
                        player.projectiles.remove(proj)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        player.cash += 5 + wave
                        player.xp += 3 + wave
                        # Random buff chance after kill
                        if random.random() < 0.1:
                            buff_type = random.choice(["damage", "speed", "firerate", "sp"])
                            player.add_buff(Buff(buff_type, 1, 10))
                    break

        # Wave system
        if not enemies:
            wave += 1
            enemies = [Enemy(wave) for _ in range(5 + wave)]

        # Draw
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        font = pygame.font.SysFont(None, 36)
        wave_text = font.render(f"Wave: {wave}", True, WHITE)
        WIN.blit(wave_text, (WIDTH - 150, 20))

        # Game Over
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
class Weapon:
    def __init__(self, name, damage, fire_rate, splash, special, cost):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.splash = splash
        self.special = special
        self.cost = cost

# Example weapons
weapons = [
    Weapon("Pistol", 5, 0.2, 0, None, 10),
    Weapon("Shotgun", 8, 0.5, 2, "spread", 20),
    Weapon("Laser", 7, 0.3, 0, "pierce", 30),
    Weapon("Cannon", 12, 0.8, 3, None, 50)
]

def open_weapon_shop(player):
    shop_open = True
    selected = 0
    font = pygame.font.SysFont(None, 28)

    while shop_open:
        WIN.fill(BLACK)
        cash_text = font.render(f"Cash: {player.cash}", True, WHITE)
        WIN.blit(cash_text, (20, 20))

        for i, weapon in enumerate(weapons):
            x, y = 50 + (i % 2) * 350, 80 + (i // 2) * 150
            color = YELLOW if i == selected else WHITE
            pygame.draw.rect(WIN, color, (x, y, 300, 120), 2)
            WIN.blit(font.render(f"{weapon.name} - Cost: {weapon.cost}", True, WHITE), (x+10, y+10))
            WIN.blit(font.render(f"Dmg:{weapon.damage} FR:{weapon.fire_rate:.2f} Splash:{weapon.splash}", True, WHITE), (x+10, y+40))
            if weapon.special:
                WIN.blit(font.render(f"Special: {weapon.special}", True, WHITE), (x+10, y+70))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    shop_open = False
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(weapons)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(weapons)
                elif event.key == pygame.K_RETURN:
                    weapon = weapons[selected]
                    if player.cash >= weapon.cost:
                        player.cash -= weapon.cost
                        player.damage = weapon.damage
                        player.shot_cooldown = weapon.fire_rate
                        player.splash = weapon.splash
                        player.special_weapon = weapon.special
import pygame, random, sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter with Dual Shops")
font = pygame.font.Font(None, 36)

# -------------------------
# CLASSES
# -------------------------
class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.speed = 5
        self.damage = 5
        self.fire_rate = 0.3
        self.splash = 0
        self.hp = 100
        self.gold = 50
        self.projectiles = []
        self.weapon = None

    def draw(self):
        pygame.draw.rect(screen, (0, 200, 0), (self.x, self.y, 40, 40))

class Enemy:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.hp = 20

    def draw(self):
        pygame.draw.rect(screen, (200, 0, 0), (self.x, self.y, 30, 30))

class Projectile:
    def __init__(self, x, y, velx, vely, damage):
        self.x, self.y = x, y
        self.velx, self.vely = velx, vely
        self.damage = damage
        self.radius = 5

    def update(self):
        self.x += self.velx
        self.y += self.vely

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

# -------------------------
# SHOPS
# -------------------------
def open_stat_shop(player):
    running = True
    while running:
        screen.fill((30, 30, 30))
        draw_text("Stat Shop (Press ESC to exit)", 50, 50)
        draw_text(f"Gold: {player.gold}", 50, 100)

        options = [
            ("1. +Speed (Cost 20)", "speed", 20),
            ("2. +Damage (Cost 30)", "damage", 30),
            ("3. +Fire Rate (Cost 25)", "fire_rate", 25),
            ("4. +Splash (Cost 40)", "splash", 40)
        ]

        for i, (txt, _, _) in enumerate(options):
            draw_text(txt, 50, 160 + i * 40)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1 and player.gold >= 20:
                    player.speed += 1; player.gold -= 20
                elif event.key == pygame.K_2 and player.gold >= 30:
                    player.damage += 2; player.gold -= 30
                elif event.key == pygame.K_3 and player.gold >= 25:
                    player.fire_rate *= 0.9; player.gold -= 25
                elif event.key == pygame.K_4 and player.gold >= 40:
                    player.splash += 1; player.gold -= 40

def open_weapon_shop(player):
    running = True
    weapons = [
        {"name": "Pistol", "cost": 20, "damage": 5, "rate": 0.3},
        {"name": "Shotgun", "cost": 40, "damage": 2, "rate": 0.6, "spread": True},
        {"name": "Sniper", "cost": 60, "damage": 15, "rate": 1.0},
        {"name": "SMG", "cost": 50, "damage": 3, "rate": 0.15}
    ]

    while running:
        screen.fill((20, 20, 50))
        draw_text("Weapon Shop (Press ESC to exit)", 50, 50)
        draw_text(f"Gold: {player.gold}", 50, 100)

        for i, w in enumerate(weapons):
            draw_text(f"{i+1}. {w['name']} (Cost {w['cost']})", 50, 160 + i * 40)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    idx = int(event.unicode) - 1
                    choice = weapons[idx]
                    if player.gold >= choice["cost"]:
                        player.weapon = choice["name"]
                        player.damage = choice["damage"]
                        player.fire_rate = choice["rate"]
                        player.gold -= choice["cost"]

# -------------------------
# UTILS
# -------------------------
def draw_text(text, x, y):
    surf = font.render(text, True, (255, 255, 255))
    screen.blit(surf, (x, y))

# -------------------------
# MAIN LOOP
# -------------------------
def main():
    clock = pygame.time.Clock()
    player = Player()
    enemies = [Enemy() for _ in range(5)]

    while True:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_LEFT]: player.x -= player.speed
        if keys[pygame.K_RIGHT]: player.x += player.speed
        if keys[pygame.K_UP]: player.y -= player.speed
        if keys[pygame.K_DOWN]: player.y += player.speed

        # Open shops
        if keys[pygame.K_s]:
            open_stat_shop(player)
        if keys[pygame.K_w]:
            open_weapon_shop(player)

        # Draw
        player.draw()
        for e in enemies: e.draw()

        draw_text(f"Gold: {player.gold}", 10, 10)
        draw_text(f"Weapon: {player.weapon}", 10, 40)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

