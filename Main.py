import pygame, sys, random, math, time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Combat Game")
FPS = 60
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0,0,0)
RED = (200,50,50)
GREEN = (0,255,0)
BLUE = (50,120,255)
YELLOW = (255,255,0)
GREY = (150,150,150)

# --- Buff Class ---
class Buff:
    def __init__(self, name, value, duration):
        self.name = name
        self.value = value
        self.end_time = time.time() + duration

# --- Weapon Class ---
class Weapon:
    def __init__(self,name,damage,fire_rate,splash,special,cost):
        self.name=name
        self.damage=damage
        self.fire_rate=fire_rate
        self.splash=splash
        self.special=special
        self.cost=cost

weapons = [
    Weapon("Pistol",5,0.3,0,None,10),
    Weapon("Shotgun",8,0.5,2,"spread",20),
    Weapon("Laser",7,0.2,0,"pierce",30),
    Weapon("Cannon",12,0.8,3,None,50)
]

# --- Projectile ---
class Projectile:
    def __init__(self,x,y,velx,vely,damage,splash):
        self.x,self.y=x,y
        self.velx,self.vely=velx,vely
        self.radius=5
        self.damage=damage
        self.splash=splash

    def update(self): self.x+=self.velx; self.y+=self.vely
    def off_screen(self): return self.x<0 or self.x>WIDTH or self.y<0 or self.y>HEIGHT
    def draw(self,win): pygame.draw.circle(win,GREEN,(int(self.x),int(self.y)),self.radius)

# --- Player ---
class Player:
    def __init__(self):
        self.x,self.y=WIDTH//2,HEIGHT//2
        self.radius=20
        self.speed=4
        self.dash_speed=12
        self.last_dash=0
        self.dash_cooldown=2
        self.last_shot=0
        self.shot_cooldown=0.3
        self.projectiles=[]
        self.max_health=100
        self.health=self.max_health
        self.xp=0; self.cash=0; self.level=1
        self.sp=1; self.splash=0; self.damage=5
        self.buffs=[]
        self.special_weapon=None

    def handle_movement(self,keys):
        dx,dy=0,0
        if keys[pygame.K_w]: dy=-self.speed
        if keys[pygame.K_s]: dy=self.speed
        if keys[pygame.K_a]: dx=-self.speed
        if keys[pygame.K_d]: dx=self.speed
        self.x+=dx; self.y+=dy
        self.x=max(self.radius,min(WIDTH-self.radius,self.x))
        self.y=max(self.radius,min(HEIGHT-self.radius,self.y))

    def dash(self,keys):
        if keys[pygame.K_e] and time.time()-self.last_dash>self.dash_cooldown:
            dx,dy=0,0
            if keys[pygame.K_w]: dy=-self.dash_speed
            if keys[pygame.K_s]: dy=self.dash_speed
            if keys[pygame.K_a]: dx=-self.dash_speed
            if keys[pygame.K_d]: dx=self.dash_speed
            self.x+=dx*self.sp; self.y+=dy*self.sp
            self.last_dash=time.time()

    def shoot(self,mouse_buttons,mouse_pos):
        if mouse_buttons[0] and time.time()-self.last_shot>self.shot_cooldown:
            mx,my=mouse_pos
            angle=math.atan2(my-self.y,mx-self.x)
            velx=math.cos(angle)*8
            vely=math.sin(angle)*8
            self.projectiles.append(Projectile(self.x,self.y,velx,vely,self.damage,self.splash))
            self.last_shot=time.time()

    def apply_buffs(self):
        for buff in self.buffs[:]:
            if time.time()>buff.end_time:
                if buff.name=="damage": self.damage-=buff.value
                elif buff.name=="speed": self.speed-=buff.value
                elif buff.name=="firerate": self.shot_cooldown+=buff.value
                elif buff.name=="sp": self.sp-=buff.value
                self.buffs.remove(buff)

    def add_buff(self,buff):
        self.buffs.append(buff)
        if buff.name=="damage": self.damage+=buff.value
        elif buff.name=="speed": self.speed+=buff.value
        elif buff.name=="firerate": self.shot_cooldown=max(0.05,self.shot_cooldown-buff.value)
        elif buff.name=="sp": self.sp+=buff.value

    def upgrade(self,stat):
        cost=10*self.level
        if self.cash>=cost:
            self.cash-=cost; self.level+=1
            if stat=="speed": self.speed+=1
            elif stat=="damage": self.damage+=2
            elif stat=="firerate": self.shot_cooldown=max(0.05,self.shot_cooldown-0.05)
            elif stat=="sp": self.sp+=1
            elif stat=="splash": self.splash+=1

    def draw(self,win):
        pygame.draw.circle(win,BLUE,(int(self.x),int(self.y)),self.radius)
        pygame.draw.circle(win,WHITE,(int(self.x),int(self.y)),self.radius,2)
        pygame.draw.rect(win,RED,(20,20,150,15))
        pygame.draw.rect(win,GREEN,(20,20,150*(self.health/self.max_health),15))
        font=pygame.font.SysFont(None,28)
        WIN.blit(font.render(f"XP:{self.xp}",True,WHITE),(20,40))
        WIN.blit(font.render(f"Cash:{self.cash}",True,WHITE),(20,65))
        for proj in self.projectiles: proj.draw(win)

# --- Enemy ---
class Enemy:
    def __init__(self,wave,etype="melee"):
        self.radius=20; self.type=etype
        self.x=random.choice([0,WIDTH]); self.y=random.randint(0,HEIGHT)
        self.speed=1.5+wave*0.2; self.max_health=30+wave*5; self.health=self.max_health
        self.last_attack=0; self.attack_cd=1.5; self.projectiles=[]
        self.is_boss=wave%10==0
        if self.is_boss: self.max_health*=5; self.health=self.max_health; self.speed*=0.8

    def update(self,player,enemies):
        move_x,move_y=0,0
        for other in enemies:
            if other!=self:
                dx=self.x-other.x; dy=self.y-other.y
                dist=math.hypot(dx,dy)
                if dist<self.radius+other.radius:
                    overlap=(self.radius+other.radius)-dist
                    move_x+=(dx/dist)*overlap*0.5
                    move_y+=(dy/dist)*overlap*0.5
        dx=player.x-self.x; dy=player.y-self.y
        dist=math.hypot(dx,dy)
      if dist != 0:
    dx = dx / dist
    dy = dy / dist
        self.x+=dx*self.speed+move_x; self.y+=dy*self.speed+move_y
        if self.type=="ranged" and time.time()-self.last_attack>self.attack_cd:
            self.shoot(player); self.last_attack=time.time()

    def shoot(self,player):
        dx,dy=player.x-self.x,player.y-self.y
        dist=math.hypot(dx,dy)
        if dist!=0: dx,dy=dx/dist,dy/dist
        self.projectiles.append(Projectile(self.x,self.y,dx*5,dy*5,5,0))

    def draw(self,win):
        color=YELLOW if self.is_boss else RED
        pygame.draw.circle(win,color,(int(self.x),int(self.y)),self.radius)
        pygame.draw.rect(win,RED,(self.x-self.radius,self.y-self.radius-10,self.radius*2,5))
        pygame.draw.rect(win,GREEN,(self.x-self.radius,self.y-self.radius-10,self.radius*2*(self.health/self.max_health),5))

# --- Shops ---
def open_stat_shop(player):
    shop_open=True; font=pygame.font.SysFont(None,32)
    while shop_open:
        WIN.fill(BLACK)
        items=[
            f"1. Speed (+1) - Cost: {10*player.level}",
            f"2. Damage (+2) - Cost: {10*player.level}",
            f"3. Fire Rate (-0.05s) - Cost: {10*player.level}",
            f"4. SP (+1 dash) - Cost: {10*player.level}",
            f"5. Splash (+1) - Cost: {10*player.level}",
            "ESC. Exit shop"
        ]
        WIN.blit(font.render(f"Cash: {player.cash}",True,WHITE),(20,20))
        for i,item in enumerate(items): WIN.blit(font.render(item,True,WHITE),(20,60+i*30))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: shop_open=False
                elif event.key==pygame.K_1: player.upgrade("speed")
                elif event.key==pygame.K_2: player.upgrade("damage")
                elif event.key==pygame.K_3: player.upgrade("firerate")
                elif event.key==pygame.K_4: player.upgrade("sp")
                elif event.key==pygame.K_5: player.upgrade("splash")

def open_weapon_shop(player):
    shop_open=True; selected=0; font=pygame.font.SysFont(None,28)
    while shop_open:
        WIN.fill(BLACK)
        WIN.blit(font.render(f"Cash: {player.cash}",True,WHITE),(20,20))
        for i,weapon in enumerate(weapons):
            x,y=50+(i%2)*350,80+(i//2)*150
            color=YELLOW if i==selected else WHITE
            pygame.draw.rect(WIN,color,(x,y,300,120),2)
            WIN.blit(font.render(f"{weapon.name} - Cost: {weapon.cost}",True,WHITE),(x+10,y+10))
            WIN.blit(font.render(f"Dmg:{weapon.damage} FR:{weapon.fire_rate:.2f} Splash:{weapon.splash}",True,WHITE),(x+10,y+40))
            if weapon.special: WIN.blit(font.render(f"Special: {weapon.special}",True,WHITE),(x+10,y+70))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: shop_open=False
                elif event.key==pygame.K_DOWN: selected=(selected+1)%len(weapons)
                elif event.key==pygame.K_UP: selected=(selected-1)%len(weapons)
                elif event.key==pygame.K_RETURN:
                    w=weapons[selected]
                    if player.cash>=w.cost:
                        player.cash-=w.cost
                        player.damage=w.damage
                        player.shot_cooldown=w.fire_rate
                        player.splash=w.splash
                        player.special_weapon=w.special

# --- Main Game ---
def main():
    player=Player(); wave=1
    enemies=[Enemy(wave) for _ in range(5)]
    running=True
    while running:
        clock.tick(FPS); WIN.fill(BLACK)
        keys=pygame.key.get_pressed(); mouse_buttons=pygame.mouse.get_pressed(); mouse_pos=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False

        if keys[pygame.K_u]: open_stat_shop(player)
        if keys[pygame.K_i]: open_weapon_shop(player)

        player.handle_movement(keys)
        player.dash(keys)
        player.shoot(mouse_buttons,mouse_pos)
        player.apply_buffs()

        # Update projectiles
        for proj in player.projectiles[:]:
            proj.update()
            if proj.off_screen(): player.projectiles.remove(proj)

        # Update enemies
        for enemy in enemies[:]:
            enemy.update(player,enemies)
            for proj in enemy.projectiles[:]:
                proj.update()
                if proj.off_screen(): enemy.projectiles.remove(proj)
                elif math.hypot(player.x-proj.x,player.y-proj.y)<player.radius+proj.radius:
                    player.health-=proj.damage
                    if proj in enemy.projectiles: enemy.projectiles.remove(proj)
            for proj in player.projectiles[:]:
                if math.hypot(enemy.x-proj.x,enemy.y-proj.y)<enemy.radius+proj.radius:
                    enemy.health-=proj.damage
                    if proj.splash>0:
                        for other in enemies:
                            if other!=enemy and math.hypot(other.x-proj.x,other.y-proj.y)<proj.splash*20:
                                other.health-=proj.damage//2
                    if proj in player.projectiles: player.projectiles.remove(proj)
                    if enemy.health<=0:
                        enemies.remove(enemy)
                        player.cash+=5+wave
                        player.xp+=3+wave
                        if random.random()<0.1: player.add_buff(Buff(random.choice(["damage","speed","firerate","sp"]),1,10))
                    break

        # Wave system
        if not enemies:
            wave+=1
            enemies=[Enemy(wave, "ranged" if random.random()<0.3 else "melee") for _ in range(5+wave)]

        # Draw
        player.draw(WIN)
        for enemy in enemies: enemy.draw(WIN)
        font=pygame.font.SysFont(None,36)
        WIN.blit(font.render(f"Wave:{wave}",True,WHITE),(WIDTH-150,20))

        # Game over
        if player.health<=0:
            WIN.blit(font.render("GAME OVER",True,RED),(WIDTH//2-80,HEIGHT//2))
            pygame.display.update()
            pygame.time.wait(2000)
            running=False

        pygame.display.update()
    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
