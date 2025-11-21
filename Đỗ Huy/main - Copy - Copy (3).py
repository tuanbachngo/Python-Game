import sys
import pygame
import math
from pygame import Rect
import random

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
        "OOOOOOOOOOOOOOOOOOOO",
        "O...................",
        "O...................",
        "O...................",
        "O...................",
        "++++++++++++++++++++",
        "~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
        "OOOOOOOOOOOOOOOOOOOO",
    ],
    [
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "S.................MC",
        "#########BB#########",
    ],
    [
        # MINI MAP 3-1
        [
            "...........O.......O",
            "...........O.......O",
            "...........O.......O",
            "...........O.......O",
            "OOOOO......O.......O",
            "OOOOO++++++O.......O",
            "OOOOO~~~~~~O.......O",
            "OOOOO~~~~~~O.......O",
            "OOOOO~~~~~~O....C..O",
            "OOOOO~~~~~~O....OOOO",
        ],
        # MINI MAP 3-2
        [
            "......OOOOOOOOO...OO",
            "......OOOOOOOOO...OO",
            "......OOOOOOOOO...OO",
            "OOOOO+++++++++++++++",###Đi về bên phải map này là đến map của cái Ánh
            "OOOOO~~~~~~~~~~~~~~~",
            "OOOOO~~~~~~~~~~~~~~~",
            "OOOOO~~~~~~~~~~~~OOO",
            "OOOOO~~~~~~~~~~~~OOO",
            "OOOOO~~~~~~~~~~~~OOO",
            "OOOOO~A~A~A~A~A~~OOO",
        ],
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
        self.image_rect = pygame.Rect(x, y, 32, 38)
        self.idle_rect = pygame.Rect(x, y, 32, 38)
        self.sit_rect  = pygame.Rect(x, y, 32, 20)
        self.rect = self.idle_rect.copy()
        self.vel_x = 0
        self.vel_y = 0
        self.swim_delay_ms = 200
        self.swim_leave_time = None
        self.pos = pygame.Vector2(x, y)
        self.on_ground = False
        self.idle_underwater = False
        self.swimming = False
        self.sit = False
        self.bubble_stunned = False
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
            "sit": load_frames("E:/Downloads/pygame_assets/sitting.png", 48, 48, 4),
            "die": load_frames("E:/Downloads/pygame_assets/dying-effect-sheet.png", 48, 48, 7),
            "swim_idle": load_frames("E:/Downloads/pygame_assets/swim_idle.png", 48, 48, 4),
            "swimming": load_frames("E:/Downloads/pygame_assets/swimming.png", 48, 48, 3),
        }
        self.state = "idle"
        self.frame_index = 0
        self.frame_speed = 0.25  # default, idle sẽ chậm
        self.image = self.animations[self.state][self.frame_index]

    def handle_input(self, keys):
        # --- Horizontal movement ---
        slow = 1
        if self.health <= 0:
            self.vel_x = 0
            return  # không di chuyển khi đã chết
        if self.bubble_stunned:
            return

        ax = 0
        if keys[pygame.K_LSHIFT] and self.on_ground:
            self.sit = True
            slow = 0.4
        else:
            self.sit = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= 1*slow
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += 1*slow
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.idle_underwater:
            self.swimming = True
            ax -= 0.2
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.idle_underwater:
            self.swimming = True
            ax += 0.2
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
        
        if self.idle_underwater and (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            self.vel_y = -2
            self.swimming = True

        if self.idle_underwater and (keys[pygame.K_s] or keys[pygame.K_DOWN]):
            self.vel_y = 2
            self.swimming = True

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
        # Cập nhật midbottom từ vị trí pos
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.swimming = False

        if self.idle_underwater:
            if abs(self.vel_x) < 0.1:
                self.state = "swim_idle"
                self.frame_speed = 0.1
            else:
                self.state = "swimming"
                self.frame_speed = 0.2
            return

        if not self.on_ground:
            self.state = "jump"
            self.frame_speed = 0.05
            return

        # Chỉ thay đổi rect khi state là idle hoặc sit
        if self.sit:
            self.state = "sit"
            self.frame_speed = 0.1
            old_midbottom = self.rect.midbottom
            self.rect = self.sit_rect.copy()
            self.rect.midbottom = old_midbottom
        else:
            self.state = "idle" if abs(self.vel_x) < 0.1 else "run"
            self.frame_speed = 0.1 if self.state == "idle" else 0.15
            if self.state == "idle":
                old_midbottom = self.rect.midbottom
                self.rect = self.idle_rect.copy()
                self.rect.midbottom = old_midbottom
    def update_animation(self):
        self.update_state()
        frames = self.animations[self.state]
        self.frame_index += self.frame_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
    def update_death_animation(self):
        if self.health <= 0:
            self.state = "die"
            frames = self.animations[self.state]
            self.frame_index += 0.1  # tốc độ animation chết
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1  # giữ frame cuối
            self.image = frames[int(self.frame_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.dead = True
    def draw(self, surface, ox = 0, oy = 0):
        surface.blit(self.image, (self.image_rect.left + ox, self.image_rect.top + 9 + oy))


# ------------------------------
# CLASS BUBBLE
# ------------------------------
class Bubble:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 2  # tốc độ cố định
        self.image = pygame.image.load("E:/Downloads/pygame_assets/bubble.png").convert_alpha()
        if self.image:
            self.rect = self.image.get_rect(center=self.pos)
            self.mask = pygame.mask.from_surface(self.image)
            self.image.set_alpha(180)
        else:
            self.rect = pygame.Rect(x, y, 24, 24)
            self.mask = None

    def update(self, dt=None):
        self.pos.x -= self.speed
        self.rect.center = (self.pos.x, self.pos.y)

    def draw(self, surface, ox=0, oy=0):
        if self.image:
            surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
        else:
            pygame.draw.circle(surface, (135, 206, 250), (int(self.pos.x + ox), int(self.pos.y + oy)), 12)
    def check_collision_with_player(self, player):
        offset = (int(player.rect.x - self.rect.x), int(player.rect.y - self.rect.y))
        if self.mask.overlap(player.mask, offset):
            player.vel_x = 0
            player.vel_y = 0
            lerp_factor = 0.1  # tỉ lệ dịch mỗi frame, 0.1 là khá mượt
            target_x, target_y = self.rect.center

            # lerp từng trục
            player.pos.x += (target_x - player.pos.x) * lerp_factor
            player.pos.y += (target_y - player.pos.y) * lerp_factor

            # cập nhật rect
            player.rect.centerx = int(player.pos.x)
            player.rect.centery = int(player.pos.y)
            player.bubble_stunned = True


class BubbleManager:
    def __init__(self, spawn_interval_ms=800, spawn_x=WIDTH, spawn_y=100):
        self.bubbles = []
        self.spawn_interval_ms = spawn_interval_ms
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_x = spawn_x + 100
        self.spawn_y = spawn_y

    def update(self, player):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time > self.spawn_interval_ms:
            self.spawn_bubble()
            self.last_spawn_time = now

        for b in self.bubbles:
            b.update()
            b.check_collision_with_player(player)
        # loại bỏ bubble ra khỏi màn hình
        self.bubbles = [b for b in self.bubbles if b.pos.x + 20 > 0]

    def spawn_bubble(self):
        bubble = Bubble(self.spawn_x, self.spawn_y)
        self.bubbles.append(bubble)

    def draw(self, surface, ox=0, oy=0):
        for b in self.bubbles:
            b.draw(surface, ox, oy)

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
# CLASS ARROW
# ------------------------------
class ArrowTrap:
    def __init__(self, x, y):
        self.x = x
        self.y = y  # vị trí gốc (đỉnh arrow khi rút xuống)
        self.width = 48
        self.max_height = 560  # chiều cao tối đa mũi tên khi đâm lên

        # Load ảnh arrow
        self.image = pygame.image.load("E:/Downloads/pygame_assets/arrow.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        # Khởi tạo rect dùng để check collide với solids
        self.rect = pygame.Rect(x, y, self.width, self.image.get_height())
        self.moving_up = True
        self.vel = -1
        self.acc = -4
        self.down_vel = 3
        self.top_y = max(self.y - self.max_height, 0)
        self.bottom_y = y
        self.activate_delay_time = 0  # thời gian delay activate ban đầu (ms)
        self.activate_start_time = pygame.time.get_ticks() + self.activate_delay_time
        self.delay_after_down_ms = 1000
        self.delay_start_time = None
    def update(self, player, solids=None):
        if solids is None:
            solids = []

        now = pygame.time.get_ticks()
        if self.activate_start_time is not None:
            if now < self.activate_start_time:  # còn delay
                return
            else:
                self.activate_start_time = None
        if self.moving_up:
            # --- Đâm lên với gia tốc ---
            self.vel += self.acc
            self.rect.y += self.vel

            # Check collision với solids
            for s in solids:
                if self.rect.colliderect(s.rect):
                    self.rect.y = max(s.rect.bottom, self.top_y)
                    self.vel = self.down_vel
                    self.moving_up = False
                    break

            # Đến đỉnh
            if self.rect.y <= self.top_y:
                self.rect.y = self.top_y
                self.vel = self.down_vel
                self.moving_up = False

        else:  # Rút xuống
            if self.delay_start_time is not None:
                # --- Đang delay ở đáy ---
                if now - self.delay_start_time >= self.delay_after_down_ms:
                    # Hết delay, chuẩn bị đâm lên
                    self.delay_start_time = None
                    self.moving_up = True
                    self.vel = -4  # khởi đầu chậm
                else:
                    return  # vẫn delay, không di chuyển
            else:
                # Di chuyển xuống đáy
                self.rect.y += self.down_vel
                if self.rect.y >= self.bottom_y - 150:
                    self.rect.y = self.bottom_y - 150
                    self.vel = 0
                    self.delay_start_time = now  # bắt đầu delay

        # Cập nhật rect để check collision
        current_height = self.bottom_y - self.rect.y if self.moving_up else self.rect.y - self.top_y
        self.rect.height = min(current_height, self.max_height)
        self.rect.width = self.width

        # Va chạm với player
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset):
            player.health -= 1

    def draw(self, surface, ox=0, oy=0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))


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
# CLASS TIDE
# ------------------------------
class Tide:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.frames = load_frames("E:/Downloads/pygame_assets/tide.png", 48, 48, 3)
        self.frame_index = 0
        self.frame_speed = 0.1
        self.image = self.frames[int(self.frame_index)]
    def update(self):
        # --- animation loop ---
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    def draw(self, surface):
        temp = self.image.copy()
        temp.set_alpha(100)
        surface.blit(temp, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS WATER Freeze
# ------------------------------
class Water:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/water.png").convert_alpha()
        self.player_inside = False

    def update(self, player: Player):
        now = pygame.time.get_ticks()
        if self.rect.colliderect(player.rect):
            # nếu chạm nước, reset timer và bật idle_underwater
            player.idle_underwater = True
            player.vel_y = 0
            player.swim_leave_time = None  # reset timer
            self.player_inside = True
        else:
            if self.player_inside:  # lần đầu ra khỏi nước
                if player.swim_leave_time is None:
                    player.swim_leave_time = now
            self.player_inside = False

            # kiểm tra delay trước khi tắt idle_underwater
            if player.swim_leave_time is not None:
                if now - player.swim_leave_time >= player.swim_delay_ms:
                    player.idle_underwater = False

    def draw(self, surface):
        temp = self.image.copy()
        temp.set_alpha(100)
        surface.blit(temp, self.rect.topleft)



# ------------------------------
# CLASS MOVING WALL
# ------------------------------
class Moving_wall:
    def __init__(self, x, y, *,
                 move_trigger_x=None,
                 fall_x=None,
                 direction=-1,        # -1: di chuyển trái, 1: di chuyển phải
                 enable_fall=True,
                 enable_broken=True):
        self.width = 67
        self.height = 288
        self.rect = pygame.Rect(x+300, y-96, self.width, self.height)
        self.rotate_image = pygame.image.load(
            "E:/Downloads/pygame_assets/full_moving_wall.png"
        ).convert_alpha()
        self.original_image = pygame.image.load(
            "E:/Downloads/pygame_assets/only_wall.png"
        ).convert_alpha()
        self.image = self.rotate_image.copy() 
        self.added_to_world = False
        # tốc độ đổ của tường
        self.angular_vel = 0
        self.angular_acc = -0.3
        # mask từ ảnh gốc
        self.mask = pygame.mask.from_surface(self.image)

        # trạng thái
        self.angle = 0
        self.triggered = False
        self.fallen = False
        self.broken = False
        self.gravity = 0.5
        self.moving_vel = 4
        self.fragments = []
        self.solid_fragments = []
        self.velocities = []

        # trigger vị trí
        self.direction = direction
        self.enable_fall = enable_fall
        self.enable_broken = enable_broken
        self.move_trigger_x = move_trigger_x if move_trigger_x is not None else x - 100
        self.fall_x = fall_x if fall_x is not None else x - 200
        

    def trigger(self, player):
        if not self.triggered and player.rect.centerx >= self.move_trigger_x:
            self.triggered = True

    def fallen_wall(self):
        pivot = self.rect.center
        rotated_image = pygame.transform.rotate(self.rotate_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=pivot)
        self.image = rotated_image
        self.rect = rotated_rect
        self.mask = pygame.mask.from_surface(self.image)

    def broken_wall(self):
        if self.broken:
            return
        self.broken = True
        self.moving_vel = 0
        x, y = self.rect.topleft
        self.fragments = [
            pygame.Rect(x, y, 44, 48),
            pygame.Rect(x, y + 48, 44, 48),
            pygame.Rect(x, y + 48*2, 44, 48)
        ]
        self.velocities = [
            [-5, -15],
            [-5, -10],
            [-10, -18]
        ]
        self.fragment_angles = [0, 0, 0]
        self.fragment_ang_vels = [30, -15, 18]
        self.fragment_images = []
        for frag in self.fragments:
            img = self.original_image.subsurface(
                frag.move(-self.rect.x, -self.rect.y)
            ).copy()
            self.fragment_images.append(img)

    def update(self, player, stone = None, solids = None, world = None):
        self.trigger(player)
        if self.triggered and not self.fallen:
            self.rect.x -= self.moving_vel
            if self.rect.x <= self.fall_x:
                self.moving_vel = 0
                self.fallen = True
                self.angle = 0

        if self.fallen and self.angle < 90 and stone.trigger3_done and not self.broken:
            self.angular_vel += self.angular_acc 
            self.angle -= self.angular_vel
            if self.angle > 90:
                self.angle = 90
            self.fallen_wall()

        if self.broken:
            all_grounded = True
            for i, frag in enumerate(self.fragments):
                vx, vy = self.velocities[i]
                vy += self.gravity
                frag.x += vx
                frag.y += vy
                self.velocities[i] = [vx, vy]
                self.fragment_angles[i] += self.fragment_ang_vels[i]
                for s in solids:
                    if frag.colliderect(s.rect):
                        frag.bottom = s.rect.top
                        self.velocities[i] = [0, 0]
                        self.fragment_ang_vels[i] = 0
                        self.solid_fragments.append(frag)
                        self.fragment_angles[i] = 90
                        self.solid_fragments.append(frag)
                        break
                if self.velocities[i][1] != 0:
                    all_grounded = False
            if all_grounded and not self.added_to_world:
                for frag in self.fragments:
                    new_block = Solid_Fragment(frag.x, frag.y)
                    self.solid_fragments.append(new_block)  # dùng cho draw/logic internal
                    world.fragments.append(new_block)          # thêm trực tiếp vào world.blocks
                self.added_to_world = True

        # collision với player
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset):
            if not self.broken:
                player.health -= 1

    def draw(self, surface, ox = 0, oy = 0):
        if not self.broken:
            surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
        else:
            for i, frag in enumerate(self.fragments):
                rotated_img = pygame.transform.rotate(self.fragment_images[i], self.fragment_angles[i])
                rotated_rect = rotated_img.get_rect(center=frag.center)
                surface.blit(rotated_img, rotated_rect.topleft)
                
# ------------------------------
# CLASS SIMPLE MOVING WALL
# ------------------------------
class SimpleMovingWall:
    def __init__(self, x, y):
        self.width = 67
        self.height = 144
        self.rect = pygame.Rect(x-70, y-96, self.width, self.height)
        # dùng asset only_wall
        self.image = pygame.image.load(
            "E:/Downloads/pygame_assets/only_wall_flipped.png"
        ).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        # trạng thái
        self.triggered = False
        self.direction = 1
        self.speed = 3
        self.move_trigger_x = 50

    def trigger(self, player):
        # trigger khi player đi qua vị trí move_trigger_x
        if not self.triggered and player.rect.centerx >= self.move_trigger_x:
            self.triggered = True

    def update(self, player):
        # kiểm tra trigger
        self.trigger(player)
        # di chuyển khi triggered
        if self.triggered:
            self.rect.x += self.speed * self.direction
            # nếu đi sang phải và biên trái chạm biên trái màn hình
            if self.rect.left >= 0 and self.direction > 0:
                self.rect.left = 0  # ép dừng đúng biên trái
                self.direction = 0  # ngăn di chuyển tiếp

    def draw(self, surface, ox=0, oy=0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
        pygame.draw.rect(surface, (0, 255, 0), 
                         pygame.Rect(self.rect.x + ox, self.rect.y + oy, self.rect.width, self.rect.height), 2)

    def check_collision_with_player(self, player):
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset):
            player.health -= 1


# ------------------------------
# CLASS BLOCK
# ------------------------------
class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/block.png").convert_alpha()

    def draw(self, surface, ox = 0, oy = 0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
# ------------------------------
# CLASS NOIMG_BLOCK
# ------------------------------
# ------------------------------
# CLASS SOLID_RECT (chỉ có rect, không cần ảnh)
# ------------------------------
class Solid_Fragment:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 44)

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
        # Ban đầu Stone nằm bên phải map
        self.pos = pygame.Vector2(x-100, y-32)
        self.vx = 0

        # Trigger flags
        self.trigger1_done = False
        self.trigger2_done = False
        self.trigger3_start = False
        self.trigger3_done = False
        self.trigger1_x = None
        self.trigger2_x = None
        self.trigger3_x = None
        # Direction sau trigger
        self.vx_trigger1 = 4
        self.vx_trigger2 = -3.5
        self.vx_trigger3 = 4

        self.image = pygame.image.load("E:/Downloads/pygame_assets/stone.png").convert_alpha()

        mask_img = pygame.image.load("E:/Downloads/pygame_assets/stonemask.png").convert_alpha()
        self.mask = pygame.mask.from_surface(mask_img)

        # rect dựa trên frame đầu tiên
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, player=None, world = None):
        if self.vx != 0:
            world.shake.start(amp=4, duration=30)
        if player:
            # TRIGGER 1
            if self.trigger1_x and not self.trigger1_done:
                if player.rect.centerx >= self.trigger1_x:
                    self.vx = self.vx_trigger1
                    self.trigger1_done = True

            # TRIGGER 2 (chỉ xảy ra sau trigger1)
            if self.trigger2_x and self.trigger1_done and not self.trigger2_done:
                if player.rect.centerx >= self.trigger2_x:
                    self.vx = self.vx_trigger2
                    self.trigger2_done = True
            if self.trigger3_x and self.trigger2_done:
    # Bắt đầu trigger 3
                if not self.trigger3_start and self.vx == 0:
                    if player.rect.centerx <= self.trigger3_x:
                        self.vx = self.vx_trigger3
                        self.trigger3_start = True

                # Kết thúc trigger 3
                if self.trigger3_start and not self.trigger3_done:
                    if self.vx == 0 and self.pos.x >= 970 + self.rect.width // 2:
                        self.trigger3_done = True
        # Di chuyển
        self.pos.x += self.vx
        self.rect.center = (self.pos.x, self.pos.y)
        if self.vx > 0:
            if self.pos.x >= 970 + self.rect.width // 2:
                self.pos.x = 970 + self.rect.width // 2
                self.vx = 0

        # Nếu đá chạy sang trái
        elif self.vx < 0:
            if self.pos.x <= self.rect.width // 2 - 50:
                self.pos.x = self.rect.width // 2 - 50
                self.vx = 0
                if self.trigger3_start and not self.trigger3_done:
                    self.trigger3_done = True
        # Va chạm với player
        if player:
            self.collide_with(player)

    def collide_with(self, other: Player):
        if self.rect.colliderect(other.rect):
            offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
            if self.mask.overlap(other.mask, offset):
                other.health -= 1

    def draw(self, surface, ox = 0, oy = 0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
# ------------------------------
# CLASS HALF BLOCK
# ------------------------------
class Half_Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y+24, 48, 24)
        self.image = pygame.image.load("E:/Downloads/pygame_assets/half_block.png").convert_alpha()

    def draw(self, surface, ox = 0, oy = 0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))

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
# CLASS SCREEN SHAKE
# ------------------------------
class ScreenShake:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.amplitude = 0
        self.time = 0

    def start(self, amp=6, duration=150):  # 150 ms rung
        self.amplitude = amp
        self.time = duration

    def update(self, dt):
        if self.time > 0:
            self.time -= dt

            # Rung random
            self.offset.x = random.randint(-self.amplitude, self.amplitude)
            self.offset.y = random.randint(-self.amplitude, self.amplitude)
        else:
            self.offset.xy = (0, 0)

    def get_offset(self):
        return self.offset.x, self.offset.y

###Hàm load trap delay
def spawn_arrow_traps(ascii_map, tile_size=TILE):
    traps = []
    now = pygame.time.get_ticks()
    for j, row in enumerate(ascii_map):
        for i, ch in enumerate(row):
            if ch == "A":
                arrow = ArrowTrap(i * tile_size, j * tile_size)
                pair_index = len(traps)
                initial_activate_delay = (pair_index % 2) * 1000
                arrow.activate_start_time = now + initial_activate_delay
                traps.append(arrow)
    return traps

# ------------------------------
# CLASS WORLD
# ------------------------------
class World:
    def __init__(self, level_index, room_index=0, bg_path=None):
        self.bubble_manager = None
        self.level_index = level_index
        self.current_room_index = room_index
        self.bg_path = bg_path
        self.shake = ScreenShake()
        self.recent_room_change_time = 0
        self.room_change_cooldown = 400
        self.load_room()  # load map hiện tại

    def get_current_map(self):
        level = LEVELS[self.level_index]
        if isinstance(level[0], list):  # mini-map
            return level[self.current_room_index]
        return level

    def load_room(self):
        ascii_map = self.get_current_map()
        bubble_spawn_found = False
        # reset các lists
        self.simple_walls = []
        self.blocks = []
        self.walls = []
        self.tides = []
        self.stones = []
        self.water = []
        self.spikes = []
        self.fragments = []
        self.c_block = []
        self.h_block = []
        self.checkpoints = []
        self.moving_walls = []
        self.arrows = []
        self.player_start = (64, 64)

        if self.bg_path:
            self.bg_image = pygame.image.load(self.bg_path).convert()
        else:
            self.bg_image = None

        for j, row in enumerate(ascii_map):
            for i, ch in enumerate(row):
                x, y = i*TILE, j*TILE
                if ch == '#':
                    self.blocks.append(Block(x, y))
                elif ch == '^':
                    self.spikes.append(Spike(x, y))
                elif ch == '+':
                    self.tides.append(Tide(x, y))
                elif ch == 'W':
                    self.walls.append(Wall(x, y))
                elif ch == 'S':
                    stone = Stone(x, y)
                    stone.trigger1_x = 90
                    stone.trigger2_x = 700
                    stone.trigger3_x = 300
                    self.stones.append(stone)
                elif ch == 'O':
                    self.c_block.append(Connected_Block(x, y))
                elif ch == 'M':
                    self.moving_walls.append(Moving_wall(x, y))
                elif ch == 'N':
                    self.simple_walls.append(SimpleMovingWall(x, y))
                elif ch == '~':
                    self.water.append(Water(x, y))
                elif ch == 'B':
                    self.h_block.append(Half_Block(x, y))
                elif ch == 'P':
                    self.player_start = (x, y)
                elif ch == 'b' and not bubble_spawn_found:
                    self.bubble_manager = BubbleManager(spawn_interval_ms=2800, spawn_x=x, spawn_y=y)
                    bubble_spawn_found = True
                if self.bubble_manager is None:
                    self.bubble_manager = BubbleManager(spawn_interval_ms=1000000)
                elif ch == 'C':
                    self.checkpoints.append(Checkpoint(x, y))
                elif ch == 'A':
                    self.water.append(Water(x, y))
                self.arrows = spawn_arrow_traps(ascii_map, TILE)


        self.player = Player(*self.player_start)


    def go_to_room(self, target_index, edge_name = None):
        self.current_room_index = target_index
        self.load_room()
        if edge_name:
            if edge_name == "left":
                self.player.rect.right = WIDTH - 50
            elif edge_name == "right":
                self.player.rect.left = 50
            elif edge_name == "top":
                self.player.rect.bottom = HEIGHT - 50
            elif edge_name == "bottom":
                self.player.rect.top = 50
    def solids(self):
        return self.blocks + self.walls + self.c_block + self.h_block + self.fragments
        

    def update(self, dt):
        for sp in self.spikes:
            sp.update(self.player)
        for cp in self.checkpoints:
            cp.update(self.player)
        for st in self.stones:
            st.update(self.player, world=self)
            for mw in self.moving_walls:
                if not mw.broken:
                    if st.rect.colliderect(mw.rect):
                        offset = (mw.rect.x - st.rect.x, mw.rect.y - st.rect.y)
                        if st.mask.overlap(mw.mask, offset):
                            if not st.trigger3_done:
                                mw.broken_wall()
        for mw in self.moving_walls:
            mw.update(self.player, stone=self.stones[0] if self.stones else None,
            solids=self.solids(), world=self)
        for smw in self.simple_walls:
            smw.update(self.player)
            smw.check_collision_with_player(self.player)
        for t in self.tides:
            t.update()
        for wa in self.water:
            wa.update(self.player)
        for arr in self.arrows:
            arr.update(self.player, self.solids())
        self.bubble_manager.update(player = self.player)
        # update screen shake WITH dt (ms)
        self.shake.update(dt)
    def draw_background(self, surface, ox = 0, oy = 0):
        if self.bg_image:
            surface.blit(self.bg_image, (ox, oy))
    def draw(self, surface):
        ox, oy = self.shake.get_offset()
        for w in self.walls:
            w.draw(surface)
        for sp in self.spikes:
            sp.draw(surface)
        for st in self.stones:
            st.draw(surface, ox, oy)
        self.player.draw(surface, ox, oy)
        for cp in self.checkpoints:
            cp.draw(surface)
        for mw in self.moving_walls:
            mw.draw(surface, ox, oy)
        for cb in self.c_block:
            cb.draw(surface)
        for t in self.tides:
            t.draw(surface)
        for hb in self.h_block:
            hb.draw(surface, ox, oy)
        for smw in self.simple_walls:
            smw.draw(surface, ox, oy)
        for b in self.blocks:
            b.draw(surface, ox, oy)
        for wa in self.water:
            wa.draw(surface)
        for arrow in self.arrows:
            arrow.draw(surface, ox, oy)
        self.bubble_manager.draw(surface, ox, oy)

# ------------------------------
# GAME LOOP
# ------------------------------

def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trap-Adventure-like")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    current_level_index = 1
    world = World(level_index=current_level_index, room_index=0, bg_path=LEVEL_BGS[current_level_index])

    edge_room_map = {
        (2, 0, "bottom"): 1,   # map 3, room 0, chạm cạnh dưới -> room 1
        (2, 1, "top"): 0,    # map 3, room 1, chạm cạnh trái -> room 0
        (2, 1, "right"): 2,   # map 3, room 1, chạm cạnh phải -> room 2
        (2, 2, "right"): 3,    # map 3, room 2, chạm cạnh trái -> room 1
        # thêm các rule khác tương tự
    }
    running = True

    def restart():
        return World(level_index=current_level_index, room_index=world.current_room_index, bg_path=LEVEL_BGS[current_level_index])

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.update(dt)
        keys = pygame.key.get_pressed()
        player = world.player
        player.handle_input(keys)
        player.apply_gravity()
        player.move_and_collide(world.solids())
        edges = {
            "left": player.rect.left <= 0,
            "right": player.rect.right >= WIDTH,
            "top": player.rect.top <= 0,
            "bottom": player.rect.bottom >= HEIGHT
        }
        now = pygame.time.get_ticks()
        for edge_name, triggered in edges.items():
            if triggered:
                key = (world.level_index, world.current_room_index, edge_name)
                if key in edge_room_map:
                    if now - world.recent_room_change_time >= world.room_change_cooldown:
                        new_room_index = edge_room_map[key]
                        world.go_to_room(new_room_index)
                        world.recent_room_change_time = now

        for cp in world.checkpoints:
            if cp.triggered and keys[pygame.K_RETURN]:
                current_level_index = (current_level_index + 1) % len(LEVELS)
                world = World(level_index=current_level_index, room_index=0, bg_path=LEVEL_BGS[current_level_index])
                break

        if player.health > 0:
            player.update_animation()
        else:
            player.update_death_animation()

        if player.dead and keys[pygame.K_r]:
            world = restart()
            player.dead = False

        ox, oy = world.shake.get_offset()
        world.draw_background(screen, ox, oy)
        world.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    run()



###Level 3 sẽ dùng camera, nhân vật phải bơi xuống dưới nước, chạm vào 1 trigger khiến mặt nước đóng băng từ từ từ dưới lên, bơi lên trên, quay lại bờ, rồi đi qua mặt nước đóng băng, chạm checkpoint -> win

###level 2: còn spike chưa vỡ hoàn chỉnh

###3 mạng cho player, nếu hết mạng thì game over chơi lại từ đầu

###1 lever kích hoạt đống băng, tích hợp lvl 1 theo code main2