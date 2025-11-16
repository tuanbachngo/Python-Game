import sys
import pygame
import math
from pygame import Rect

# ------------------------------
# CÀI ĐẶT CƠ BẢN
# ------------------------------
WIDTH, HEIGHT = 960, 480
FPS = 60
TILE = 48

GRAVITY = 0.32
MAX_FALL = 14
PLAYER_SPEED = 3
JUMP_VEL = 9

WHITE = (240, 240, 240)
BG = (20, 24, 28)

# ------------------------------
# BẢN ĐỒ ASCII
# ------------------------------
LEVELS = [
    [
        "....................",
        "#..................O",
        "#..................O",
        "#..................O",
        "#..................O",
        "O..................O",
        "O..................O",
        "O..................O",
        "O...S........P......",
        "######O#############",
    ],
    [
        "####################",
        "#..................#",
        "#..^...............#",
        "#...........#####..#",
        "#..................#",
        "#......P...........#",
        "#..........^.......#",
        "#..............C...#",
        "#..................#",
        "####################",
    ]
]

LEVEL_BGS = [
    "E:/Downloads/pygame_assets/bg-1.png",
    "E:/Downloads/pygame_assets/bg-2.png",
    "E:/Downloads/pygame_assets/bg-3.png"
]
# ------------------------------
# HÀM LOAD FRAME
# ------------------------------
def load_frames(sheet_path, frame_w, frame_h, num_frames):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(i*frame_w, 0, frame_w, frame_h))
        frames.append(frame)
    return frames

# ------------------------------
# CLASS PLAYER
# ------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = Rect(x-8, y, 32, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.pos = pygame.Vector2(x, y)
        self.on_ground = False
        self.health = 1
        self.ori_image = pygame.image.load("E:/Downloads/pygame_assets/mask_state.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.ori_image)
        self.facing_right = True
        self.dead = False

        # --- Animation frames ---
        self.animations = {
            "idle": load_frames("E:/Downloads/pygame_assets/idle-effect-sheet.png", 48, 48, 9),
            "run": load_frames("E:/Downloads/pygame_assets/running-effect-sheet.png", 48, 48, 4),
            "jump": load_frames("E:/Downloads/pygame_assets/jumping-effect-sheet.png", 48, 48, 3),
            "die": load_frames("E:/Downloads/pygame_assets/dying-effect-sheet.png", 48, 48, 7)
        }

        self.state = "idle"
        self.frame_index = 0
        self.frame_speed = 0.25  # default, idle sẽ chậm
        self.image = self.animations[self.state][self.frame_index]

    def handle_input(self, keys):
        # --- Horizontal movement ---
        if self.health <= 0:
            self.vel_x = 0
            return  # không di chuyển khi đã chết

        ax = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += 1
        self.vel_x = ax * PLAYER_SPEED

        # --- Facing direction ---
        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False

        # --- Jump ---
        if self.on_ground and (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            self.vel_y = -JUMP_VEL
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)

    def move_and_collide(self, solids):
        # Mặc định là không chạm đất
        self.on_ground = False
        prev_rect = self.rect.copy()
        # ---- DI CHUYỂN NGANG (X) ----
        self.rect.x += float(self.vel_x)
        for s in solids:
            if self.rect.colliderect(s.rect):
                if self.vel_x > 0:  # va phải
                    self.rect.right = s.rect.left
                elif self.vel_x < 0:  # va trái
                    self.rect.left = s.rect.right

        # ---- DI CHUYỂN DỌC (Y) ----
        self.rect.y += float(self.vel_y)
        for s in solids:
            if self.rect.colliderect(s):
                # Rơi xuống và chạm mặt đất
                if prev_rect.bottom <= s.rect.top and self.vel_y >= 0:
                    self.rect.bottom = s.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # Nhảy lên và đụng trần
                elif prev_rect.top >= s.rect.bottom and self.vel_y <= 0:
                    self.rect.top = s.rect.bottom
                    self.vel_y = 0

        # ---- CHECK NỀN DƯỚI CHÂN ----
        if not self.on_ground:
            for s in solids:
                if s.rect.colliderect(self.rect.move(0, 1)):
                    self.on_ground = True
                    break
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery


    def update_state(self):
    # Nếu đang nhảy hoặc rơi
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if not self.on_ground:
            self.state = "jump"
            self.frame_speed = 0.12
        else:
            if abs(self.vel_x) > 0.1:
                self.state = "run"
                self.frame_speed = 0.15
            else:
                self.state = "idle"
                self.frame_speed = 0.6

    def update_animation(self):
        self.update_state()
        frames = self.animations[self.state]
        self.frame_index += self.frame_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update_death_animation(self):
        if self.health <= 0:
            self.state = "die"
            frames = self.animations[self.state]
            self.frame_index += 0.2  # tốc độ animation chết
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1  # giữ frame cuối
            self.image = frames[int(self.frame_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.dead = True

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x-8, self.rect.y))



# ------------------------------
# CLASS SPIKE
# ------------------------------
class Spike:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 36, 36)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/trap-1.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, player: Player):
        if self.rect.colliderect(player.rect):
            offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
            if self.mask.overlap(player.mask, offset):
                player.health -= 1
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x-5, self.rect.y))

# ------------------------------
# CLASS CHECKPOINT
# ------------------------------
class Checkpoint:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 48, 48)
        self.frames = load_frames("E:/Downloads/pygame_assets/activated-checkpoint-sheet.png", 48, 48, 3)
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = self.frames[int(self.frame_index)]
        self.triggered = False
        self.touch_time = None
        self.activated = False
        self.delay_ms = 100

    def activate(self):
        self.activated = True
        self.triggered = True
        print("Checkpoint ready: Press ENTER to continue!")

    def update(self, player: "Player"):
        now = pygame.time.get_ticks()
        # --- animation loop ---
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # --- check collision để bắt đầu timer ---
        if self.rect.colliderect(player.rect) and not self.activated:
            if self.touch_time is None:
                self.touch_time = now
        # --- kiểm tra đủ delay ---
        if self.touch_time is not None and not self.activated:
            if now - self.touch_time >= self.delay_ms:
                player.vel_x = 0
                player.vel_y = 0
                self.activate()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# ------------------------------
# CLASS HOVER BOARD
# ------------------------------


# ------------------------------
# CLASS RISING TIDE
# ------------------------------


# ------------------------------
# CLASS MOVING WALL
# ------------------------------
class Moving_wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y-96, 96, 96)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/full_moving_wall.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 90
        self.pivot = x+48, y
        self.broken = False
        self.fallen = False
        self.trigger_cond = False
        self.moving_vel = 0.9
        self.gravity = 0.5
        self.broken_parts = []
        self.vels = []
        self.original_image = self.image
        self.initial = self.rect.x
    def trigger(self):
        if self.trigger_cond == False:
            return
        self.rect.x -= self.moving_vel
        if self.rect.x == self.initial - 191.7:
            return
    def fallen_wall(self):
        if self.fallen:
            return
        self.fallen = True
        rotated_image = pygame.transform.rotate(self.original_image, -90)
        rotated_rect = rotated_image.get_rect()
        offset = pygame.Vector2(self.rect.topleft) - self.pivot
        offset = offset.rotate(90)
        new_pos = self.pivot + offset
        self.image = rotated_image
        self.rect = rotated_rect
        self.rect.topleft = (new_pos.x, new_pos.y)

    def broken_wall(self):
        if self.broken:
            return
        self.broken = False
        x , y = self.rect.topleft
        self.broken_parts = [
            pygame.Rect(x, y, 96, 48),
            pygame.Rect(x, y+48, 96, 48),
            pygame.Rect(x, y+96, 96, 48),
            pygame.Rect(x, y+144, 96, 48)
        ]
        self.vels = [
            [-5, 10],
            [10, 5],
            [-6, 2],
            [-12, 4]
        ]

    def update(self, player: Player):
        if self.broken:
            for i, rect in enumerate(self.fragments):
                vx, vy = self.velocities[i]
                vy += self.gravity
                rect.x += vx
                rect.y += vy
                self.velocities[i][1] = vy
        if self.rect.colliderect(player.rect):
            offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
            if self.mask.overlap(player.mask, offset):
                player.health -= 1
        if self.fallen and self.angle < 90:
            self.angle += 2
            self.fallen_wall(self.angle)
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
            
# ------------------------------
# CLASS BLOCK
# ------------------------------
class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/block.png").convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# ------------------------------
# CLASS CONNECTED_BLOCK
# ------------------------------
class Connected_Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/connected_block.png").convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# ------------------------------
# CLASS ROLLING_STONE
# ------------------------------

class Stone:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x-96, y-31)
        self.vx = 0
        self.direction = 1

        self.frames = load_frames(
            "E:/Downloads/pygame_assets/stone.png",
            frame_w=162, frame_h=159, num_frames=6
        )
        self.frame_index = 0
        self.frame_speed = 0.1
        self.image = pygame.image.load("E:/Downloads/pygame_assets/stonemask.png").convert_alpha()
        mask_img = pygame.image.load("E:/Downloads/pygame_assets/stonemask.png").convert_alpha()
        self.mask = pygame.mask.from_surface(mask_img)

        # rect dựa trên frame đầu tiên
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, player=None):
        # Move
        self.pos.x += self.vx
        self.rect.center = (self.pos.x, self.pos.y)

        # animation
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
        # collision
        if player:
            self.collide_with(player)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collide_with(self, other: Player):
        if self.rect.colliderect(other.rect):
            offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
            if self.mask.overlap(other.mask, offset):
                other.health -= 1

# ------------------------------
# CLASS WALL
# ------------------------------
class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 19)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/wall.png").convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# ------------------------------
# CLASS WORLD
# ------------------------------
class World:
    def __init__(self, ascii_map, bg_path=None):
        self.blocks = []
        self.walls = []
        self.stones = []
        self.spikes = []
        self.c_block = []
        self.checkpoints = []
        self.moving_walls = []
        self.player_start = (64, 64)

        if bg_path:
            self.bg_image = pygame.image.load(bg_path).convert()
        else:
            self.bg_image = None

        for j, row in enumerate(ascii_map):
            for i, ch in enumerate(row):
                x, y = i*TILE, j*TILE
                if ch == '#':
                    self.blocks.append(Block(x, y))
                elif ch == '^':
                    self.spikes.append(Spike(x, y))
                elif ch == 'W':
                    self.walls.append(Wall(x, y))
                elif ch == 'S':
                    self.stones.append(Stone(x, y))
                elif ch == 'O':
                    self.c_block.append(Connected_Block(x, y))
                elif ch == 'M':
                    self.moving_walls.append(Moving_wall(x, y))
                elif ch == 'O':
                    self.player_start = (x, y)
                elif ch == 'C':
                    self.checkpoints.append(Checkpoint(x, y))

        self.player = Player(*self.player_start)

    def solids(self):
        return self.blocks + self.walls + self.c_block

    def update(self):
        for sp in self.spikes:
            sp.update(self.player)
        for cp in self.checkpoints:
            cp.update(self.player)
        for st in self.stones:
            st.update(self.player)

    def draw_background(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0,0))
    def draw(self, surface):
        for b in self.blocks:
            b.draw(surface)
        for w in self.walls:
            w.draw(surface)
        for sp in self.spikes:
            sp.draw(surface)
        for st in self.stones:
            st.draw(surface)
        for cp in self.checkpoints:
            cp.draw(surface)
        for mw in self.moving_walls:
            mw.draw(surface)
        for cb in self.c_block:
            cb.draw(surface)
        self.player.draw(surface)

# ------------------------------
# GAME LOOP
# ------------------------------
def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trap-Adventure-like")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    current_level_index = 0
    world = World(LEVELS[current_level_index], bg_path=LEVEL_BGS[current_level_index])
    running = True

    def restart(current_level_index):
        return World(
            LEVELS[current_level_index],
            bg_path=LEVEL_BGS[current_level_index]
        )

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        world.update()
        keys = pygame.key.get_pressed()
        player = world.player
        player.handle_input(keys)
        player.apply_gravity()
        player.move_and_collide(world.solids())
        for cp in world.checkpoints:
            if cp.triggered and keys[pygame.K_RETURN]:
                current_level_index = (current_level_index + 1) % len(LEVELS)
                world = World(LEVELS[current_level_index], bg_path=LEVEL_BGS[current_level_index])
                break

        if player.health > 0:
            player.update_animation()
        else:
            player.update_death_animation()
        if player.dead and keys[pygame.K_r]:
            world = restart(current_level_index)
            player.dead = False

    # DRAW
        world.draw_background(screen)
        world.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    run()



###Level 3 sẽ dùng camera, nhân vật phải bơi xuống dưới nước, chạm vào 1 trigger khiến mặt nước đóng băng từ từ từ dưới lên, bơi lên trên, quay lại bờ, rồi đi qua mặt nước đóng băng, chạm checkpoint -> win

###level 2: đá lăn, moving wall, spike

###3 mạng cho player, nếu hết mạng thì game over chơi lại từ đầu