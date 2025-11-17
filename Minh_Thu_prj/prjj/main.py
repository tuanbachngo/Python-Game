import sys
import pygame
from pygame import Rect
from pathlib import Path

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
        "####################",
        "#..................#",
        "#..................#",
        "#..................#",
        "#..................#",
        "#..................#",
        "#.......#.....M....#",
        "#.P................#",
        "#########........H.C",
        "#########^^^^^^^^###",
        "####################",
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
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

ASSETS_DIR = BASE_DIR / "pygame_assets"

def asset(name: str) -> str:
    return str(ASSETS_DIR / name)

LEVEL_BGS = [
    asset("bg-1.png"),
    asset("bg-2.png"),
    asset("bg-3.png"),
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
        self.rect = Rect(x, y, 32, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = 1
        self.facing_right = True
        self.dead = False

        # --- Animation frames ---
        self.animations = {
            "idle": load_frames(asset("idle-effect-sheet.png"), 48, 48, 9),
            "run": load_frames(asset("running-effect-sheet.png"), 48, 48, 4),
            "jump": load_frames(asset("jumping-effect-sheet.png"), 48, 48, 3),
            "die": load_frames(asset("dying-effect-sheet.png"), 48, 48, 7)
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
        self.rect.x += int(self.vel_x)
        for s in solids:
            if self.rect.colliderect(s.rect):
                if self.vel_x > 0:  # va phải
                    self.rect.right = s.rect.left
                elif self.vel_x < 0:  # va trái
                    self.rect.left = s.rect.right

        # ---- DI CHUYỂN DỌC (Y) ----
        self.rect.y += int(self.vel_y)
        for s in solids:
            if self.rect.colliderect(s.rect):
                # Rơi xuống và chạm mặt đất
                if prev_rect.bottom <= s.rect.top and self.vel_y >= 0:
                    self.rect.bottom = s.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    if isinstance(s, MovingPlatform):
                        vel = s.get_velocity()
                        self.rect.x += int(vel.x)
                        self.rect.y += int(vel.y)
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


    def update_state(self):
    # Nếu đang nhảy hoặc rơi
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
        surface.blit(self.image, self.rect.topleft)
# ------------------------------
# CLASS SPIKE
# ------------------------------
class Spike:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 48, 48)
        self.image = pygame.image.load(asset("trap-1.png")).convert_alpha()

    def update(self, player: Player):
        if self.rect.colliderect(player.rect):
                player.health -= 1
                player.vel_y = -8 
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
class HiddenSpike(Spike):
    """Bẫy ẩn: ban đầu vô hình, khi player chạm thì hiện hình và gây chết ngay."""
    def __init__(self, x, y, one_time=True):
        super().__init__(x, y)
        self.visible = False          # ban đầu ẩn
        self.one_time = one_time
        self.triggered = False

    def update(self, player: "Player"):
        if self.rect.colliderect(player.rect):
            if not self.triggered:
                self.visible = True    # hiển thị gai ngay lập tức
                player.health = 0      # chết ngay
                player.vel_y = -12      # hiệu ứng bật nhẹ
                print(f"[HiddenSpike] Bẫy bật tại ({self.rect.x}, {self.rect.y})")
                if self.one_time:
                    self.triggered = True

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS CHECKPOINT
# ------------------------------
class Checkpoint:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 48, 48)
        self.frames = load_frames(asset("activated-checkpoint-sheet.png"), 48, 48, 3)
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
# CLASS BLOCK
# ------------------------------
class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load(asset("block.png")).convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS PLATFORM
class MovingPlatform(Block):
    def __init__(self, x, y, dx=2, dy=0, move_range=100):
        super().__init__(x, y)
        self.start_x = x
        self.start_y = y
        self.dx = dx      # tốc độ di chuyển theo trục X
        self.dy = dy      # tốc độ di chuyển theo trục Y
        self.move_range = move_range
        self.direction = 1
        self.prev_pos = pygame.Vector2(self.rect.x, self.rect.y) # lưu lại vị trí của platform ở frame trước
    def update(self):
        # Lưu vị trí cũ để tính độ dịch chuyển
        self.prev_pos.update(self.rect.x, self.rect.y)

        # Cập nhật vị trí
        self.rect.x += self.dx * self.direction
        self.rect.y += self.dy * self.direction

        # Nếu vượt quá phạm vi di chuyển thì đảo hướng
        if abs(self.rect.x - self.start_x) >= self.move_range or abs(self.rect.y - self.start_y) >= self.move_range:
            self.direction *= -1

    def get_velocity(self):
        # Trả về độ dịch chuyển của platform giữa 2 frame
        return pygame.Vector2(self.rect.x - self.prev_pos.x, self.rect.y - self.prev_pos.y)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))  
# ------------------------------
# CLASS WORLD
# ------------------------------
class World:
    def __init__(self, ascii_map, bg_path=None):
        self.blocks = []
        self.platform = []
        self.spikes = []
        self.triggers = []
        self.checkpoints = []
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
                elif ch == 'P':
                    self.player_start = (x, y)
                elif ch == 'C':
                    self.checkpoints.append(Checkpoint(x, y))
                elif ch == 'M':
                    self.blocks.append(MovingPlatform(x,y,dx=2,dy=1,move_range=150))
                elif ch == 'H':  # bẫy ẩn
                    self.spikes.append(HiddenSpike(x, y))   
        self.player = Player(*self.player_start)

    def solids(self):
        return self.blocks

    def update(self):
        for b in self.blocks:
            if isinstance(b, MovingPlatform):
                    b.update()
        for sp in self.spikes:
            sp.update(self.player)
        for cp in self.checkpoints:
            cp.update(self.player)

    def draw_background(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0,0))
    def draw(self, surface):
        for b in self.blocks:
            b.draw(surface)
        for sp in self.spikes:
            sp.draw(surface)
        for cp in self.checkpoints:
            cp.draw(surface)
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

    def restart():
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
            world = restart()
            player.dead = False

    # DRAW
        world.draw_background(screen)
        world.draw(screen)

        health_surf = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_surf, (16,16))

        pygame.display.flip()


if __name__ == "__main__":
    run()
