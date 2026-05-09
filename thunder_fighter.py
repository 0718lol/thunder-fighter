"""
雷霆战机 - 关卡制飞机大战
操作说明：
  方向键/WASD - 移动
  空格键 - 射击（自动射击已开启）
  P - 暂停
  R - 重新开始
  ESC - 退出
"""
import pygame
import random
import sys
import math

# ==================== 初始化 ====================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("雷霆战机 - 关卡制飞机大战")
clock = pygame.time.Clock()
FPS = 60

# ==================== 颜色定义 ====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
PURPLE = (180, 50, 255)
CYAN = (50, 255, 255)
DARK_BG = (10, 10, 30)
GRAY = (100, 100, 100)

# ==================== 字体 ====================
import os
# 尝试加载系统中文字体
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",   # 黑体
    "C:/Windows/Fonts/simsun.ttc",   # 宋体
]
font_path = None
for fp in font_paths:
    if os.path.exists(fp):
        font_path = fp
        break

if font_path:
    font_small = pygame.font.Font(font_path, 18)
    font_medium = pygame.font.Font(font_path, 28)
    font_large = pygame.font.Font(font_path, 48)
    font_title = pygame.font.Font(font_path, 60)
else:
    font_small = pygame.font.Font(None, 22)
    font_medium = pygame.font.Font(None, 32)
    font_large = pygame.font.Font(None, 52)
    font_title = pygame.font.Font(None, 64)


# ==================== 绘制飞机形状 ====================
def draw_player_ship(surface, x, y, level=1):
    """绘制玩家飞机"""
    cx, cy = x, y
    # 主机身
    points = [(cx, cy - 30), (cx - 18, cy + 15), (cx - 8, cy + 10),
              (cx, cy + 20), (cx + 8, cy + 10), (cx + 18, cy + 15)]
    color = CYAN if level < 3 else YELLOW if level < 5 else ORANGE
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 2)
    # 驾驶舱
    pygame.draw.circle(surface, WHITE, (cx, cy - 10), 5)
    pygame.draw.circle(surface, BLUE, (cx, cy - 10), 3)
    # 引擎火焰
    flame_len = random.randint(8, 18)
    flame_color = random.choice([ORANGE, YELLOW, RED])
    pygame.draw.polygon(surface, flame_color,
                        [(cx - 6, cy + 20), (cx, cy + 20 + flame_len), (cx + 6, cy + 20)])
    # 机翼装饰
    if level >= 2:
        pygame.draw.line(surface, YELLOW, (cx - 18, cy + 15), (cx - 28, cy + 5), 3)
        pygame.draw.line(surface, YELLOW, (cx + 18, cy + 15), (cx + 28, cy + 5), 3)
    if level >= 4:
        pygame.draw.line(surface, PURPLE, (cx - 14, cy + 10), (cx - 24, cy), 2)
        pygame.draw.line(surface, PURPLE, (cx + 14, cy + 10), (cx + 24, cy), 2)


def draw_enemy_ship(surface, x, y, etype="normal"):
    """绘制敌机"""
    cx, cy = x, y
    if etype == "normal":
        points = [(cx, cy + 20), (cx - 14, cy - 12), (cx - 6, cy - 8),
                  (cx, cy - 16), (cx + 6, cy - 8), (cx + 14, cy - 12)]
        pygame.draw.polygon(surface, RED, points)
        pygame.draw.polygon(surface, WHITE, points, 1)
    elif etype == "fast":
        points = [(cx, cy + 18), (cx - 10, cy - 10), (cx, cy - 14), (cx + 10, cy - 10)]
        pygame.draw.polygon(surface, GREEN, points)
        pygame.draw.polygon(surface, WHITE, points, 1)
    elif etype == "tank":
        pygame.draw.rect(surface, ORANGE, (cx - 16, cy - 14, 32, 28), border_radius=6)
        pygame.draw.rect(surface, WHITE, (cx - 16, cy - 14, 32, 28), 2, border_radius=6)
        pygame.draw.circle(surface, RED, (cx, cy), 6)
    elif etype == "boss":
        # 大型Boss
        pygame.draw.rect(surface, PURPLE, (cx - 50, cy - 35, 100, 70), border_radius=10)
        pygame.draw.rect(surface, WHITE, (cx - 50, cy - 35, 100, 70), 3, border_radius=10)
        pygame.draw.circle(surface, RED, (cx, cy - 5), 12)
        pygame.draw.circle(surface, WHITE, (cx, cy - 5), 8)
        pygame.draw.circle(surface, YELLOW, (cx, cy - 5), 4)
        # 炮台
        pygame.draw.rect(surface, GRAY, (cx - 40, cy + 20, 15, 15))
        pygame.draw.rect(surface, GRAY, (cx + 25, cy + 20, 15, 15))
        pygame.draw.rect(surface, GRAY, (cx - 8, cy + 25, 16, 12))


def draw_bullet(surface, x, y, color=CYAN, is_player=True):
    """绘制子弹"""
    if is_player:
        pygame.draw.rect(surface, color, (x - 2, y - 6, 4, 12), border_radius=2)
        pygame.draw.rect(surface, WHITE, (x - 1, y - 4, 2, 8), border_radius=1)
    else:
        pygame.draw.circle(surface, color, (int(x), int(y)), 6)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), 3)
        pygame.draw.circle(surface, (255, 150, 150), (int(x), int(y)), 4)


def draw_star(surface, x, y, size):
    """绘制星星背景"""
    brightness = random.randint(100, 255)
    color = (brightness, brightness, brightness)
    pygame.draw.circle(surface, color, (int(x), int(y)), size)


def draw_powerup(surface, x, y, ptype):
    """绘制道具"""
    colors = {"health": RED, "weapon": YELLOW, "shield": CYAN, "bomb": ORANGE}
    color = colors.get(ptype, WHITE)
    pygame.draw.rect(surface, color, (x - 12, y - 12, 24, 24), border_radius=6)
    pygame.draw.rect(surface, WHITE, (x - 12, y - 12, 24, 24), 2, border_radius=6)
    label = {"health": "+", "weapon": "W", "shield": "S", "bomb": "B"}
    text = font_small.render(label.get(ptype, "?"), True, BLACK)
    surface.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))


# ==================== 游戏对象类 ====================
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.width = 40
        self.height = 40
        self.speed = 6
        self.hp = 100
        self.max_hp = 100
        self.weapon_level = 1
        self.score = 0
        self.shield = 0
        self.bombs = 3
        self.shoot_delay = 150
        self.last_shot = 0
        self.invincible = 0
        self.alive = True

    def update(self, keys):
        if not self.alive:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        self.x = max(20, min(WIDTH - 20, self.x))
        self.y = max(40, min(HEIGHT - 20, self.y))
        if self.invincible > 0:
            self.invincible -= 1

    def shoot(self):
        if not self.alive:
            return []
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return []
        self.last_shot = now
        bullets = []
        bx, by = self.x, self.y - 25
        if self.weapon_level == 1:
            bullets.append(Bullet(bx, by, 0, -10, CYAN, True))
        elif self.weapon_level == 2:
            bullets.append(Bullet(bx - 8, by, 0, -10, CYAN, True))
            bullets.append(Bullet(bx + 8, by, 0, -10, CYAN, True))
        elif self.weapon_level == 3:
            bullets.append(Bullet(bx, by, 0, -12, YELLOW, True))
            bullets.append(Bullet(bx - 12, by + 5, -1, -10, CYAN, True))
            bullets.append(Bullet(bx + 12, by + 5, 1, -10, CYAN, True))
        elif self.weapon_level >= 4:
            bullets.append(Bullet(bx - 6, by, 0, -12, YELLOW, True))
            bullets.append(Bullet(bx + 6, by, 0, -12, YELLOW, True))
            bullets.append(Bullet(bx - 16, by + 8, -2, -9, ORANGE, True))
            bullets.append(Bullet(bx + 16, by + 8, 2, -9, ORANGE, True))
        return bullets

    def draw(self, surface):
        if not self.alive:
            return
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        draw_player_ship(surface, self.x, self.y, self.weapon_level)
        if self.shield > 0:
            pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), 28, 2)
            pygame.draw.circle(surface, (*CYAN[:3],), (int(self.x), int(self.y)), 30, 1)

    def draw_ui(self, surface):
        # HP条
        pygame.draw.rect(surface, GRAY, (10, 10, 160, 16), border_radius=3)
        hp_width = max(0, int(160 * self.hp / self.max_hp))
        hp_color = GREEN if self.hp > 50 else YELLOW if self.hp > 25 else RED
        pygame.draw.rect(surface, hp_color, (10, 10, hp_width, 16), border_radius=3)
        pygame.draw.rect(surface, WHITE, (10, 10, 160, 16), 2, border_radius=3)
        hp_text = font_small.render(f"HP: {self.hp}/{self.max_hp}", True, WHITE)
        surface.blit(hp_text, (14, 10))
        # 分数
        score_text = font_small.render(f"分数: {self.score}", True, WHITE)
        surface.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        # 武器等级
        weapon_text = font_small.render(f"武器: Lv.{self.weapon_level}", True, YELLOW)
        surface.blit(weapon_text, (10, 32))
        # 炸弹
        bomb_text = font_small.render(f"炸弹: {self.bombs}", True, ORANGE)
        surface.blit(bomb_text, (WIDTH - bomb_text.get_width() - 10, 32))
        # 护盾
        if self.shield > 0:
            shield_text = font_small.render(f"护盾: {self.shield // 60 + 1}s", True, CYAN)
            surface.blit(shield_text, (10, 54))


class Bullet:
    def __init__(self, x, y, dx, dy, color=CYAN, is_player=True):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.is_player = is_player
        self.alive = True
        self.damage = 20 if is_player else 10

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.y < -10 or self.y > HEIGHT + 10 or self.x < -10 or self.x > WIDTH + 10:
            self.alive = False

    def draw(self, surface):
        draw_bullet(surface, self.x, self.y, self.color, self.is_player)


class Enemy:
    def __init__(self, etype="normal", level=1):
        self.etype = etype
        self.alive = True
        self.move_timer = 0
        self.shoot_timer = random.randint(20, 60)

        if etype == "normal":
            self.x = random.randint(30, WIDTH - 30)
            self.y = random.randint(-80, -30)
            self.width, self.height = 28, 28
            self.hp = 20 + level * 5
            self.max_hp = self.hp
            self.speed = 1.5 + level * 0.2
            self.score = 10 + level * 2
            self.shoot_chance = 80 + level * 10
        elif etype == "fast":
            self.x = random.randint(30, WIDTH - 30)
            self.y = random.randint(-100, -40)
            self.width, self.height = 20, 20
            self.hp = 10 + level * 3
            self.max_hp = self.hp
            self.speed = 3 + level * 0.3
            self.score = 15 + level * 3
            self.shoot_chance = 100
        elif etype == "tank":
            self.x = random.randint(40, WIDTH - 40)
            self.y = random.randint(-100, -50)
            self.width, self.height = 32, 28
            self.hp = 60 + level * 15
            self.max_hp = self.hp
            self.speed = 0.8 + level * 0.1
            self.score = 30 + level * 5
            self.shoot_chance = 60 + level * 5
        elif etype == "boss":
            self.x = WIDTH // 2
            self.y = -60
            self.width, self.height = 100, 70
            self.hp = 300 + level * 200
            self.max_hp = self.hp
            self.speed = 1.0
            self.score = 200 + level * 100
            self.shoot_chance = 25
            self.phase = 0
            self.target_y = 100

    def update(self):
        if self.etype == "boss":
            if self.y < self.target_y:
                self.y += 1
            else:
                self.move_timer += 1
                self.x += math.sin(self.move_timer * 0.02) * 2
                self.x = max(60, min(WIDTH - 60, self.x))
        elif self.etype == "fast":
            self.y += self.speed
            self.x += math.sin(self.y * 0.05) * 2
        else:
            self.y += self.speed
            self.move_timer += 1
            if self.move_timer % 120 < 60:
                self.x += 0.5
            else:
                self.x -= 0.5

        if self.y > HEIGHT + 50:
            self.alive = False

    def try_shoot(self):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            min_val = min(self.shoot_chance, max(15, self.shoot_chance - 40))
            max_val = max(self.shoot_chance, min_val + 10)
            self.shoot_timer = random.randint(min_val, max_val)
            if self.etype == "boss":
                bullets = []
                for angle in [-30, -15, 0, 15, 30]:
                    rad = math.radians(90 + angle)
                    dx = math.cos(rad) * 4
                    dy = math.sin(rad) * 4
                    bullets.append(Bullet(self.x, self.y + 35, dx, dy, PURPLE, False))
                return bullets
            else:
                return [Bullet(self.x, self.y + 15, 0, 4 + self.speed, RED, False)]
        return []

    def draw(self, surface):
        draw_enemy_ship(surface, self.x, self.y, self.etype)
        if self.etype != "boss" and self.hp < self.max_hp:
            bar_w = 30
            bar_x = self.x - bar_w // 2
            bar_y = self.y - 22
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, 4))
            hp_w = max(0, int(bar_w * self.hp / self.max_hp))
            pygame.draw.rect(surface, RED, (bar_x, bar_y, hp_w, 4))
        elif self.etype == "boss":
            bar_w = 200
            bar_x = WIDTH // 2 - bar_w // 2
            bar_y = 70
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, 12), border_radius=3)
            hp_w = max(0, int(bar_w * self.hp / self.max_hp))
            pygame.draw.rect(surface, RED, (bar_x, bar_y, hp_w, 12), border_radius=3)
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 12), 2, border_radius=3)
            boss_text = font_small.render(f"BOSS", True, WHITE)
            surface.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, bar_y - 20))


class PowerUp:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.ptype = ptype
        self.speed = 2
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        draw_powerup(surface, self.x, self.y, self.ptype)


class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.dx = random.uniform(-4, 4)
        self.dy = random.uniform(-4, 4)
        self.life = random.randint(15, 35)
        self.max_life = self.life
        self.color = color or random.choice([RED, ORANGE, YELLOW, WHITE])
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1
        self.life -= 1
        self.dx *= 0.98
        self.dy *= 0.98

    def draw(self, surface):
        alpha = self.life / self.max_life
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2.5)
        self.size = random.choice([1, 1, 1, 2, 2, 3])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        draw_star(surface, self.x, self.y, self.size)


# ==================== 关卡配置 ====================
LEVELS = {
    1: {"name": "银河前线", "enemies": [("normal", 15)], "spawn_rate": 60, "boss": False},
    2: {"name": "星际突袭", "enemies": [("normal", 10), ("fast", 8)], "spawn_rate": 50, "boss": False},
    3: {"name": "暗影危机", "enemies": [("normal", 8), ("fast", 8), ("tank", 4)], "spawn_rate": 45, "boss": False},
    4: {"name": "深渊之门", "enemies": [("normal", 10), ("fast", 8), ("tank", 5)], "spawn_rate": 40, "boss": True},
    5: {"name": "终极决战", "enemies": [("normal", 12), ("fast", 10), ("tank", 6)], "spawn_rate": 35, "boss": True},
    6: {"name": "无尽深渊", "enemies": [("normal", 15), ("fast", 12), ("tank", 8)], "spawn_rate": 30, "boss": True},
}


# ==================== 游戏主类 ====================
class Game:
    def __init__(self):
        self.state = "menu"  # menu, help, playing, paused, level_clear, game_over, victory
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []
        self.stars = [Star() for _ in range(80)]
        self.current_level = 1
        self.level_config = LEVELS[self.current_level]
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.total_enemies = sum(c for _, c in self.level_config["enemies"])
        self.spawn_timer = 0
        self.boss_spawned = False
        self.boss_defeated = False
        self.level_clear_timer = 0
        self.screen_shake = 0
        self.flash_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.message = ""
        self.message_timer = 0
        self.help_scroll = 0

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []
        self.current_level = 1
        self.level_config = LEVELS[self.current_level]
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.total_enemies = sum(c for _, c in self.level_config["enemies"])
        self.spawn_timer = 0
        self.boss_spawned = False
        self.boss_defeated = False
        self.level_clear_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.state = "playing"
        self.show_message(f"第{self.current_level}关: {self.level_config['name']}")

    def next_level(self):
        self.current_level += 1
        if self.current_level > max(LEVELS.keys()):
            self.state = "victory"
            return
        self.level_config = LEVELS[min(self.current_level, max(LEVELS.keys()))]
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.total_enemies = sum(c for _, c in self.level_config["enemies"])
        self.spawn_timer = 0
        self.boss_spawned = False
        self.boss_defeated = False
        self.level_clear_timer = 0
        self.enemies = []
        self.bullets = []
        self.player.hp = min(self.player.max_hp, self.player.hp + 30)
        self.player.weapon_level = min(5, self.player.weapon_level + 1)
        self.player.bombs = min(5, self.player.bombs + 1)
        self.state = "playing"
        self.show_message(f"第{self.current_level}关: {self.level_config['name']}")

    def show_message(self, msg):
        self.message = msg
        self.message_timer = 120

    def spawn_enemy(self):
        if self.enemies_spawned >= self.total_enemies:
            if not self.boss_spawned and self.level_config.get("boss", False):
                boss = Enemy("boss", self.current_level)
                self.enemies.append(boss)
                self.boss_spawned = True
                self.show_message("BOSS 出现！")
            return

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_timer = self.level_config["spawn_rate"]
            available = []
            for etype, count in self.level_config["enemies"]:
                spawned_count = sum(1 for e in self.enemies if e.etype == etype)
                if spawned_count < count * 2:
                    available.append(etype)
            if available:
                etype = random.choice(available)
                self.enemies.append(Enemy(etype, self.current_level))
                self.enemies_spawned += 1

    def spawn_powerup(self, x, y):
        if random.random() < 0.15:
            ptype = random.choice(["health", "weapon", "shield", "bomb"])
            self.powerups.append(PowerUp(x, y, ptype))

    def create_explosion(self, x, y, count=15, color=None):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
        self.screen_shake = max(self.screen_shake, 5)

    def use_bomb(self):
        if self.player.bombs <= 0:
            return
        self.player.bombs -= 1
        self.flash_timer = 15
        self.screen_shake = 15
        for enemy in self.enemies:
            damage = 100 if enemy.etype != "boss" else 200
            enemy.hp -= damage
            self.create_explosion(enemy.x, enemy.y, 20, ORANGE)
        for bullet in self.bullets:
            if not bullet.is_player:
                bullet.alive = False
        self.show_message("全屏炸弹！")

    def check_collisions(self):
        # 玩家子弹 vs 敌机
        for bullet in self.bullets:
            if not bullet.is_player or not bullet.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                dx = abs(bullet.x - enemy.x)
                dy = abs(bullet.y - enemy.y)
                if dx < enemy.width // 2 + 4 and dy < enemy.height // 2 + 4:
                    bullet.alive = False
                    enemy.hp -= bullet.damage
                    self.create_explosion(bullet.x, bullet.y, 3, CYAN)
                    if enemy.hp <= 0:
                        enemy.alive = False
                        self.enemies_killed += 1
                        self.player.score += enemy.score
                        self.combo += 1
                        self.combo_timer = 120
                        self.max_combo = max(self.max_combo, self.combo)
                        if enemy.etype == "boss":
                            self.create_explosion(enemy.x, enemy.y, 50, PURPLE)
                            self.boss_defeated = True
                            self.player.score += 500
                            self.show_message("BOSS 击败！")
                        else:
                            self.create_explosion(enemy.x, enemy.y, 12)
                            self.spawn_powerup(enemy.x, enemy.y)
                    break

        # 敌机子弹 vs 玩家
        if self.player.invincible <= 0 and self.player.alive:
            for bullet in self.bullets:
                if bullet.is_player or not bullet.alive:
                    continue
                dx = abs(bullet.x - self.player.x)
                dy = abs(bullet.y - self.player.y)
                if dx < 18 and dy < 20:
                    bullet.alive = False
                    if self.player.shield > 0:
                        self.player.shield -= 30
                        self.create_explosion(bullet.x, bullet.y, 5, CYAN)
                    else:
                        self.player.hp -= bullet.damage
                        self.create_explosion(bullet.x, bullet.y, 8, RED)
                        self.screen_shake = 8
                        self.combo = 0
                    if self.player.hp <= 0:
                        self.player.alive = False
                        self.create_explosion(self.player.x, self.player.y, 40, ORANGE)
                        self.state = "game_over"
                    break

        # 敌机 vs 玩家（碰撞）
        if self.player.invincible <= 0 and self.player.alive:
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                dx = abs(enemy.x - self.player.x)
                dy = abs(enemy.y - self.player.y)
                if dx < (enemy.width // 2 + 15) and dy < (enemy.height // 2 + 15):
                    if self.player.shield > 0:
                        self.player.shield -= 60
                    else:
                        self.player.hp -= 30
                        self.screen_shake = 10
                    if enemy.etype != "boss":
                        enemy.hp = 0
                        enemy.alive = False
                        self.create_explosion(enemy.x, enemy.y, 15)
                    self.create_explosion(self.player.x, self.player.y, 10, RED)
                    self.player.invincible = 60
                    self.combo = 0
                    if self.player.hp <= 0:
                        self.player.alive = False
                        self.create_explosion(self.player.x, self.player.y, 40, ORANGE)
                        self.state = "game_over"
                    break

        # 玩家拾取道具
        for powerup in self.powerups:
            if not powerup.alive:
                continue
            dx = abs(powerup.x - self.player.x)
            dy = abs(powerup.y - self.player.y)
            if dx < 25 and dy < 25:
                powerup.alive = False
                if powerup.ptype == "health":
                    self.player.hp = min(self.player.max_hp, self.player.hp + 30)
                    self.show_message("HP +30")
                elif powerup.ptype == "weapon":
                    self.player.weapon_level = min(5, self.player.weapon_level + 1)
                    self.show_message(f"武器升级 Lv.{self.player.weapon_level}")
                elif powerup.ptype == "shield":
                    self.player.shield = 300
                    self.show_message("护盾激活！")
                elif powerup.ptype == "bomb":
                    self.player.bombs = min(5, self.player.bombs + 1)
                    self.show_message("炸弹 +1")
                self.create_explosion(powerup.x, powerup.y, 8, GREEN)

    def update(self):
        # 更新星空背景
        for star in self.stars:
            star.update()

        # 更新粒子
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # 屏幕震动衰减
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # 消息计时
        if self.message_timer > 0:
            self.message_timer -= 1

        # 连击计时
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # 自动射击
        new_bullets = self.player.shoot()
        self.bullets.extend(new_bullets)

        # 敌机生成
        self.spawn_enemy()

        # 更新子弹
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # 更新敌机
        for enemy in self.enemies:
            enemy.update()
            new_bullets = enemy.try_shoot()
            self.bullets.extend(new_bullets)
        self.enemies = [e for e in self.enemies if e.alive]

        # 更新道具
        for powerup in self.powerups:
            powerup.update()
        self.powerups = [p for p in self.powerups if p.alive]

        # 碰撞检测
        self.check_collisions()

        # 关卡通关判定
        if self.boss_defeated:
            self.level_clear_timer += 1
            if self.level_clear_timer > 120:
                self.state = "level_clear"
        elif not self.level_config.get("boss", False):
            # 所有敌机已生成且场上没有敌机时通关
            if self.enemies_spawned >= self.total_enemies and len(self.enemies) == 0:
                self.state = "level_clear"

    def draw_menu(self, surface):
        surface.fill(DARK_BG)
        for star in self.stars:
            star.draw(surface)

        # 标题
        title = font_title.render("雷霆战机", True, CYAN)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        subtitle = font_medium.render("关卡制飞机大战", True, WHITE)
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 200))

        # 操作说明
        controls = [
            "方向键 / WASD - 移动",
            "空格 - 发射炸弹",
            "P - 暂停",
            "R - 重新开始",
        ]
        for i, text in enumerate(controls):
            t = font_small.render(text, True, GRAY)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 300 + i * 25))

        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()

        # 开始按钮
        self.start_btn = pygame.Rect(WIDTH // 2 - 100, 430, 200, 50)
        color = (100, 255, 100) if self.start_btn.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(surface, color, self.start_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.start_btn, 3, border_radius=10)
        start_text = font_medium.render("开始游戏", True, WHITE)
        surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 440))

        # 游戏说明按钮
        self.help_btn = pygame.Rect(WIDTH // 2 - 100, 500, 200, 50)
        color = (100, 150, 255) if self.help_btn.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(surface, color, self.help_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.help_btn, 3, border_radius=10)
        help_text = font_medium.render("游戏说明", True, WHITE)
        surface.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 510))

        # 退出按钮
        self.quit_btn = pygame.Rect(WIDTH // 2 - 100, 570, 200, 50)
        color = (255, 100, 100) if self.quit_btn.collidepoint(mouse_pos) else RED
        pygame.draw.rect(surface, color, self.quit_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.quit_btn, 3, border_radius=10)
        quit_text = font_medium.render("退出游戏", True, WHITE)
        surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 580))

    def draw_help(self, surface):
        surface.fill(DARK_BG)
        for star in self.stars:
            star.draw(surface)

        # 创建滚动区域
        if not hasattr(self, 'help_scroll'):
            self.help_scroll = 0

        # 标题（固定）
        title = font_large.render("游戏说明", True, CYAN)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

        # 滚动提示
        scroll_hint = font_small.render("滚轮/↑↓键滚动", True, GRAY)
        surface.blit(scroll_hint, (WIDTH // 2 - scroll_hint.get_width() // 2, 55))

        # 内容区域（可滚动）
        content_y = 80 - self.help_scroll

        # 操作按键
        section_title = font_medium.render("操作按键", True, YELLOW)
        surface.blit(section_title, (30, content_y))
        content_y += 35
        controls = [
            ("方向键/WASD", "移动飞机"),
            ("空格键", "释放全屏炸弹（清屏！）"),
            ("P", "暂停游戏"),
            ("R", "重新开始"),
            ("ESC", "退出游戏"),
            ("ENTER", "开始/下一关"),
        ]
        for key, desc in controls:
            key_text = font_small.render(key, True, WHITE)
            desc_text = font_small.render(f"- {desc}", True, GRAY)
            surface.blit(key_text, (40, content_y))
            surface.blit(desc_text, (180, content_y))
            content_y += 25

        # 道具说明
        content_y += 15
        section_title = font_medium.render("道具说明", True, YELLOW)
        surface.blit(section_title, (30, content_y))
        content_y += 35
        powerups = [
            ("红色 +", "HP回复30点", RED),
            ("黄色 W", "武器升级（最高5级）", YELLOW),
            ("青色 S", "护盾（抵挡伤害）", CYAN),
            ("橙色 B", "炸弹+1", ORANGE),
        ]
        for name, desc, color in powerups:
            name_text = font_small.render(name, True, color)
            desc_text = font_small.render(f"- {desc}", True, GRAY)
            surface.blit(name_text, (40, content_y))
            surface.blit(desc_text, (140, content_y))
            content_y += 25

        # 敌机说明
        content_y += 15
        section_title = font_medium.render("敌机类型", True, YELLOW)
        surface.blit(section_title, (30, content_y))
        content_y += 35
        enemies = [
            ("红色", "普通敌机，速度慢", RED),
            ("绿色", "高速敌机，速度快但血少", GREEN),
            ("橙色方块", "坦克，血厚但速度慢", ORANGE),
            ("紫色大方块", "BOSS，发射扇形弹幕！", PURPLE),
        ]
        for name, desc, color in enemies:
            name_text = font_small.render(name, True, color)
            desc_text = font_small.render(f"- {desc}", True, GRAY)
            surface.blit(name_text, (40, content_y))
            surface.blit(desc_text, (140, content_y))
            content_y += 25

        # 通关条件
        content_y += 15
        section_title = font_medium.render("通关条件", True, YELLOW)
        surface.blit(section_title, (30, content_y))
        content_y += 35
        tips = [
            "第1-3关：消灭所有敌机即可通关",
            "第4-6关：需要击败BOSS才能通关",
        ]
        for tip in tips:
            tip_text = font_small.render(tip, True, WHITE)
            surface.blit(tip_text, (40, content_y))
            content_y += 25

        # 返回按钮（固定底部）
        self.back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 60, 200, 45)
        pygame.draw.rect(surface, GRAY, self.back_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.back_btn, 2, border_radius=10)
        back_text = font_small.render("返回主菜单", True, WHITE)
        surface.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 52))

    def draw_playing(self, surface):
        # 偏移（屏幕震动）
        ox = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        oy = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        surface.fill(DARK_BG)
        for star in self.stars:
            star.draw(surface)

        # 创建临时surface用于震动效果
        temp = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for powerup in self.powerups:
            powerup.draw(temp)
        for bullet in self.bullets:
            bullet.draw(temp)
        for enemy in self.enemies:
            enemy.draw(temp)
        self.player.draw(temp)
        for p in self.particles:
            p.draw(temp)

        surface.blit(temp, (ox, oy))

        # UI
        self.player.draw_ui(surface)

        # 关卡信息
        level_text = font_small.render(f"第{self.current_level}关: {self.level_config['name']}", True, WHITE)
        surface.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))

        # 连击显示
        if self.combo > 1:
            combo_text = font_medium.render(f"{self.combo} COMBO!", True, YELLOW)
            surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 85))

        # 消息显示
        if self.message_timer > 0:
            msg_text = font_medium.render(self.message, True, YELLOW)
            alpha = min(255, self.message_timer * 4)
            surface.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT // 2 - 100))

        # 闪屏效果
        if self.flash_timer > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, self.flash_timer * 15))
            surface.blit(flash, (0, 0))

    def draw_paused(self, surface):
        self.draw_playing(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        pause_text = font_large.render("暂停", True, WHITE)
        surface.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 40))
        hint = font_small.render("按 P 继续", True, GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

    def draw_level_clear(self, surface):
        self.draw_playing(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        clear_text = font_large.render("关卡通过！", True, GREEN)
        surface.blit(clear_text, (WIDTH // 2 - clear_text.get_width() // 2, HEIGHT // 2 - 80))

        level_text = font_medium.render(f"第{self.current_level}关: {self.level_config['name']}", True, WHITE)
        surface.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 20))

        score_text = font_small.render(f"当前分数: {self.player.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))

        combo_text = font_small.render(f"最高连击: {self.max_combo}", True, ORANGE)
        surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, HEIGHT // 2 + 60))

        # 下一关按钮
        self.next_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(surface, GREEN, self.next_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.next_btn, 3, border_radius=10)
        next_text = font_medium.render("下一关", True, WHITE)
        surface.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 110))

    def draw_game_over(self, surface):
        self.draw_playing(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        go_text = font_large.render("游戏结束", True, RED)
        surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 80))

        score_text = font_medium.render(f"最终分数: {self.player.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 10))

        level_text = font_small.render(f"到达第{self.current_level}关", True, WHITE)
        surface.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 + 30))

        combo_text = font_small.render(f"最高连击: {self.max_combo}", True, ORANGE)
        surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, HEIGHT // 2 + 60))

        # 重新开始按钮
        self.restart_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(surface, GREEN, self.restart_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.restart_btn, 3, border_radius=10)
        restart_text = font_medium.render("重新开始", True, WHITE)
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 110))

        # 退出按钮
        self.quit_btn2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 170, 200, 50)
        pygame.draw.rect(surface, RED, self.quit_btn2, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.quit_btn2, 3, border_radius=10)
        quit_text = font_medium.render("退出游戏", True, WHITE)
        surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 180))

    def draw_victory(self, surface):
        surface.fill(DARK_BG)

        # 星空背景
        for star in self.stars:
            star.draw(surface)

        # 持续产生彩色粒子
        if random.random() < 0.5:
            color = random.choice([YELLOW, CYAN, GREEN, PURPLE, ORANGE, RED])
            self.particles.append(Particle(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 250), color))
        for p in self.particles:
            p.update()
            p.draw(surface)
        self.particles = [p for p in self.particles if p.life > 0]

        # 顶部装饰线
        pygame.draw.line(surface, YELLOW, (50, 60), (WIDTH - 50, 60), 3)
        pygame.draw.line(surface, CYAN, (50, 65), (WIDTH - 50, 65), 2)

        # 大标题 "通关！"
        t = pygame.time.get_ticks()
        bounce = int(math.sin(t * 0.005) * 5)
        vic_text = font_title.render("通关！", True, YELLOW)
        surface.blit(vic_text, (WIDTH // 2 - vic_text.get_width() // 2, 90 + bounce))

        # 副标题
        congrats = font_medium.render("恭喜通关全部6关！", True, WHITE)
        surface.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, 170))

        # 统计面板背景
        panel = pygame.Rect(40, 210, WIDTH - 80, 160)
        pygame.draw.rect(surface, (30, 30, 60), panel, border_radius=12)
        pygame.draw.rect(surface, CYAN, panel, 2, border_radius=12)

        # 统计数据
        stats_y = 225
        stats = [
            ("最终分数", f"{self.player.score}", YELLOW),
            ("最高连击", f"{self.max_combo} COMBO", ORANGE),
            ("到达关卡", f"第{self.current_level}关 全部通关", GREEN),
            ("武器等级", f"Lv.{self.player.weapon_level}", PURPLE),
        ]
        for label, value, color in stats:
            label_text = font_small.render(label, True, GRAY)
            value_text = font_small.render(value, True, color)
            surface.blit(label_text, (70, stats_y))
            surface.blit(value_text, (220, stats_y))
            stats_y += 35

        # 评价
        score = self.player.score
        if score >= 5000:
            rank = "S"
            rank_color = YELLOW
            rank_text = "传说级飞行员！"
        elif score >= 3000:
            rank = "A"
            rank_color = GREEN
            rank_text = "精英飞行员！"
        elif score >= 1500:
            rank = "B"
            rank_color = CYAN
            rank_text = "优秀飞行员！"
        else:
            rank = "C"
            rank_color = WHITE
            rank_text = "继续加油！"

        # 评级区域背景（脉冲效果）
        t = pygame.time.get_ticks()
        pulse = abs(math.sin(t * 0.003)) * 0.5 + 0.5
        rank_panel = pygame.Rect(WIDTH // 2 - 60, 385, 120, 80)
        pygame.draw.rect(surface, (50, 50, 80), rank_panel, border_radius=15)
        pygame.draw.rect(surface, rank_color, rank_panel, 3, border_radius=15)
        # 发光效果
        glow = pygame.Surface((120, 80), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*rank_color[:3], int(50 * pulse)), (0, 0, 120, 80), border_radius=15)
        surface.blit(glow, (WIDTH // 2 - 60, 385))

        # 评级文字
        rank_text_render = font_title.render(rank, True, rank_color)
        surface.blit(rank_text_render, (WIDTH // 2 - rank_text_render.get_width() // 2, 395))

        # 评级说明
        rank_desc = font_medium.render(rank_text, True, rank_color)
        surface.blit(rank_desc, (WIDTH // 2 - rank_desc.get_width() // 2, 480))

        # 底部装饰线
        pygame.draw.line(surface, YELLOW, (50, 500), (WIDTH - 50, 500), 3)
        pygame.draw.line(surface, CYAN, (50, 505), (WIDTH - 50, 505), 2)

        # 再玩一次按钮
        self.restart_btn = pygame.Rect(WIDTH // 2 - 100, 525, 200, 45)
        pygame.draw.rect(surface, GREEN, self.restart_btn, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.restart_btn, 2, border_radius=10)
        restart_text = font_medium.render("再玩一次", True, WHITE)
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 533))

        # 退出按钮
        self.quit_btn2 = pygame.Rect(WIDTH // 2 - 100, 585, 200, 45)
        pygame.draw.rect(surface, RED, self.quit_btn2, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.quit_btn2, 2, border_radius=10)
        quit_text = font_medium.render("退出游戏", True, WHITE)
        surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 593))

    def draw(self, surface):
        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "help":
            self.draw_help(surface)
        elif self.state == "playing":
            self.draw_playing(surface)
        elif self.state == "paused":
            self.draw_paused(surface)
        elif self.state == "level_clear":
            self.draw_level_clear(surface)
        elif self.state == "game_over":
            self.draw_game_over(surface)
        elif self.state == "victory":
            self.draw_victory(surface)

    def handle_event(self, event):
        # 鼠标点击处理
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.state == "menu":
                if hasattr(self, 'start_btn') and self.start_btn.collidepoint(mouse_pos):
                    self.reset()
                elif hasattr(self, 'help_btn') and self.help_btn.collidepoint(mouse_pos):
                    self.help_scroll = 0
                    self.state = "help"
                elif hasattr(self, 'quit_btn') and self.quit_btn.collidepoint(mouse_pos):
                    return False
            elif self.state == "help":
                if hasattr(self, 'back_btn') and self.back_btn.collidepoint(mouse_pos):
                    self.state = "menu"

        # 鼠标滚轮滚动
        if event.type == pygame.MOUSEWHEEL:
            if self.state == "help":
                self.help_scroll = max(0, self.help_scroll - event.y * 30)
            elif self.state == "victory":
                if hasattr(self, 'restart_btn') and self.restart_btn.collidepoint(mouse_pos):
                    self.reset()
                elif hasattr(self, 'quit_btn2') and self.quit_btn2.collidepoint(mouse_pos):
                    return False
            elif self.state == "game_over":
                if hasattr(self, 'restart_btn') and self.restart_btn.collidepoint(mouse_pos):
                    self.reset()
                elif hasattr(self, 'quit_btn2') and self.quit_btn2.collidepoint(mouse_pos):
                    return False
            elif self.state == "level_clear":
                if hasattr(self, 'next_btn') and self.next_btn.collidepoint(mouse_pos):
                    self.next_level()

        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.reset()
                elif event.key == pygame.K_h:
                    self.help_scroll = 0
                    self.state = "help"
                elif event.key == pygame.K_v:  # 调试：直接看胜利画面
                    self.player.score = 5500
                    self.max_combo = 42
                    self.current_level = 6
                    self.state = "victory"
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif self.state == "help":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_h:
                    self.state = "menu"
                elif event.key == pygame.K_UP:
                    self.help_scroll = max(0, self.help_scroll - 30)
                elif event.key == pygame.K_DOWN:
                    self.help_scroll += 30

            elif self.state == "playing":
                if event.key == pygame.K_p:
                    self.state = "paused"
                elif event.key == pygame.K_SPACE:
                    self.use_bomb()
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif self.state == "paused":
                if event.key == pygame.K_p:
                    self.state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif self.state == "level_clear":
                if event.key == pygame.K_RETURN:
                    self.next_level()
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif self.state == "game_over":
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif self.state == "victory":
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False

        return True


# ==================== 主循环 ====================
def main():
    game = Game()
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not game.handle_event(event):
                    running = False

            game.update()
            game.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    except Exception as e:
        # 出错时显示错误信息
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        # 在屏幕上显示错误
        screen.fill((0, 0, 0))
        error_lines = str(e).split('\n')
        for i, line in enumerate(error_lines[:10]):
            text = font_small.render(line, True, (255, 50, 50))
            screen.blit(text, (20, 50 + i * 25))
        hint = font_small.render("按 ESC 退出", True, (200, 200, 200))
        screen.blit(hint, (20, 300))
        pygame.display.flip()
        # 等待用户按ESC退出
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
