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
        "#.............M....#",
        "#.P.....#............",
        "##########....#..H.C",
        "##########^^^^^^^###",
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

ASSETS_DIR = Path(r"C:\Users\Admin\Downloads\Python\CODE\Trap Adventure\pygame_assets") 
def asset(name: str) -> str:
    return (ASSETS_DIR / name).as_posix() 

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
# CLASS GAME STATE
# ------------------------------
class GameState:
    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

# ------------------------------
# CLASS SETTINGS
# ------------------------------
class GameSettings:
    def __init__(self):
        self.difficulty = "NORMAL"  # EASY, NORMAL, HARD
        self.music_volume = 0.7
       # self.sfx_volume = 0.8
        self.show_fps = True
        
    def apply_difficulty(self):
        global PLAYER_SPEED, JUMP_VEL, GRAVITY
        
        if self.difficulty == "EASY":
            PLAYER_SPEED = 4
            JUMP_VEL = 10
            GRAVITY = 0.28
        elif self.difficulty == "NORMAL":
            PLAYER_SPEED = 3
            JUMP_VEL = 9
            GRAVITY = 0.32
        elif self.difficulty == "HARD":
            PLAYER_SPEED = 2.5
            JUMP_VEL = 8
            GRAVITY = 0.36
# ------------------------------
# CLASS MENU MANAGER
# ------------------------------
class MenuManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 32)
        self.font_small = pygame.font.SysFont("consolas", 24)
        
        self.main_menu_options = ["START GAME", "SETTINGS", "QUIT"]
        self.settings_options = ["DIFFICULTY", "MUSIC VOLUME", "SFX VOLUME", "SHOW FPS", "BACK"]
        self.difficulty_options = ["EASY", "NORMAL", "HARD"]
        
        self.selected_index = 0
        self.in_settings = False
        self.in_difficulty_menu = False
        
    def draw_main_menu(self, surface, settings):
        # Background
        surface.fill((20, 24, 28))
        
        # Title
        title_text = self.font_large.render("TRAP ADVENTURE", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 100))
        surface.blit(title_text, title_rect)
        
        # Menu options
        for i, option in enumerate(self.main_menu_options):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width//2, 250 + i * 60))
            surface.blit(text, rect)
            
            # Vẽ indicator cho option được chọn
            if i == self.selected_index:
                pygame.draw.polygon(surface, (255, 215, 0), [
                    (rect.left - 30, rect.centery),
                    (rect.left - 10, rect.centery - 10),
                    (rect.left - 10, rect.centery + 10)
                ])
        
        # Footer
        footer_text = self.font_small.render("Use ARROW KEYS to navigate, ENTER to select", True, (200, 200, 200))
        footer_rect = footer_text.get_rect(center=(self.screen_width//2, self.screen_height - 50))
        surface.blit(footer_text, footer_rect)
    
    def draw_settings_menu(self, surface, settings):
        surface.fill((30, 35, 40))
        
        # Title
        title_text = self.font_large.render("SETTINGS", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        surface.blit(title_text, title_rect)
        
        if self.in_difficulty_menu:
            self.draw_difficulty_menu(surface, settings)
            return
        
        # Settings options
        for i, option in enumerate(self.settings_options):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(midleft=(self.screen_width//2 - 100, 200 + i * 60))
            surface.blit(text, rect)
            
            # Hiển thị giá trị setting
            value_text = self.get_setting_value(option, settings)
            value_surf = self.font_medium.render(value_text, True, (100, 200, 255))
            value_rect = value_surf.get_rect(midleft=(self.screen_width//2 + 50, 200 + i * 60))
            surface.blit(value_surf, value_rect)
            
            if i == self.selected_index:
                pygame.draw.polygon(surface, (255, 215, 0), [
                    (rect.left - 30, rect.centery),
                    (rect.left - 10, rect.centery - 10),
                    (rect.left - 10, rect.centery + 10)
                ])
    
    def draw_difficulty_menu(self, surface, settings):
        title_text = self.font_medium.render("SELECT DIFFICULTY", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 150))
        surface.blit(title_text, title_rect)
        
        for i, difficulty in enumerate(self.difficulty_options):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            if difficulty == settings.difficulty:
                color = (100, 255, 100)  # Màu xanh cho độ khó đang chọn
            
            text = self.font_medium.render(difficulty, True, color)
            rect = text.get_rect(center=(self.screen_width//2, 250 + i * 60))
            surface.blit(text, rect)
            
            if i == self.selected_index:
                pygame.draw.circle(surface, (255, 215, 0), (rect.left - 20, rect.centery), 8)
    
    def get_setting_value(self, option, settings):
        if option == "DIFFICULTY":
            return settings.difficulty
        return ""
    
    def handle_input(self, event, settings, game_state):
        if event.type == pygame.KEYDOWN:
            if self.in_difficulty_menu:
                return self.handle_difficulty_input(event, settings)
            else:
                return self.handle_settings_input(event, settings, game_state)
        return game_state
    
    def handle_difficulty_input(self, event, settings):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.difficulty_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.difficulty_options)
        elif event.key == pygame.K_RETURN:
            settings.difficulty = self.difficulty_options[self.selected_index]
            settings.apply_difficulty()
            self.in_difficulty_menu = False
            self.selected_index = 0
        elif event.key == pygame.K_ESCAPE:
            self.in_difficulty_menu = False
            self.selected_index = 0
        return GameState.SETTINGS
    
    def handle_settings_input(self, event, settings, game_state):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.settings_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.settings_options)
        elif event.key == pygame.K_RETURN:
            selected_option = self.settings_options[self.selected_index]
            
            if selected_option == "DIFFICULTY":
                self.in_difficulty_menu = True
                self.selected_index = self.difficulty_options.index(settings.difficulty)
            elif selected_option == "MUSIC VOLUME":
                settings.music_volume = (settings.music_volume + 0.1) % 1.1
            elif selected_option == "SFX VOLUME":
                settings.sfx_volume = (settings.sfx_volume + 0.1) % 1.1
            elif selected_option == "SHOW FPS":
                settings.show_fps = not settings.show_fps
            elif selected_option == "BACK":
                self.selected_index = 0
                return GameState.MAIN_MENU
                
        elif event.key == pygame.K_ESCAPE:
            self.selected_index = 0
            return GameState.MAIN_MENU
            
        return game_state
# ------------------------------
# CLASS HUD
# ------------------------------
class HUD:
    def __init__(self, player, settings):
        self.player = player
        self.settings = settings
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
        
        # Tạo menu manager
        self.menu_manager = MenuManager(WIDTH, HEIGHT)
    
    def draw_ingame_hud(self, surface, current_level, total_levels):
        # Background HUD
        hud_bg = pygame.Rect(10, 10, 250, 100)
        pygame.draw.rect(surface, (0, 0, 0, 180), hud_bg, border_radius=10)
        pygame.draw.rect(surface, WHITE, hud_bg, 2, border_radius=10)
        
        # Health
        health_text = f"Health: {self.player.health}"
        health_surf = self.font.render(health_text, True, WHITE)
        surface.blit(health_surf, (30, 25))
        
        # Level
        level_text = f"Level: {current_level + 1}/{total_levels}"
        level_surf = self.font.render(level_text, True, WHITE)
        surface.blit(level_surf, (30, 55))
        
        # Difficulty
        diff_text = f"Difficulty: {self.settings.difficulty}"
        diff_surf = self.small_font.render(diff_text, True, (200, 200, 100))
        surface.blit(diff_surf, (30, 85))
        
        # FPS (nếu bật)
        if self.settings.show_fps:
            fps_text = f"FPS: {pygame.time.Clock().get_fps():.1f}"
            fps_surf = self.small_font.render(fps_text, True, (150, 150, 255))
            surface.blit(fps_surf, (WIDTH - 100, 20))
    
    def draw_menu(self, surface, game_state):
        if game_state == GameState.MAIN_MENU:
            self.menu_manager.draw_main_menu(surface, self.settings)
        elif game_state == GameState.SETTINGS:
            self.menu_manager.draw_settings_menu(surface, self.settings)
    
    def handle_menu_input(self, event, game_state):
        return self.menu_manager.handle_input(event, self.settings, game_state)
# ------------------------------
# CLASS PLAYER
# ------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 36 , 46)
        self.vel_x = 0
        self.vel_y = 0
        self.pos = pygame.Vector2(x, y)
        self.on_ground = False
        self.health = 1
        self.ori_image = pygame.image.load(asset("mask_state.png")).convert_alpha()
        self.mask = pygame.mask.from_surface(self.ori_image)
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
            ax -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += 1.0
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
            if self.rect.colliderect(s.rect):
                # Rơi xuống và chạm mặt đất
                if prev_rect.bottom <= s.rect.top and self.vel_y >= 0:
                    self.rect.bottom = s.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    # THÊM: Xử lý platform di chuyển
                    if hasattr(s, 'get_velocity'):  # Kiểm tra nếu là platform di chuyển
                        vel = s.get_velocity()
                        self.rect.x += float(vel.x)
                        self.rect.y += float(vel.y)
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
        
        # Cập nhật vector vị trí từ rect (giữ nguyên của code 2)
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery

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
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS SPIKE
# ------------------------------
class Spike:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 36, 36)
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
    def __init__(self, x, y, world_ref = None, level_id=0):
        self.rect = Rect(x, y, 48, 48)
        self.frames = load_frames(asset("activated-checkpoint-sheet.png"), 48, 48, 3)
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = self.frames[int(self.frame_index)]
        self.touch_time = None
        self.activated = False
        self.delay_ms = 0
        self.health = 1
        self.active = True
        self.world_ref = world_ref
        self.level_id = level_id
       # --- hiệu ứng fade ---
        self.fade_alpha = 255
        self.fading_out = False
        self.fading_in = False
        self.fade_speed = 10  # tốc độ mờ dần mỗi frame

    def take_damage(self):
        self.health -= 1
        if self.health <= 0 and not self.fading_out:
            self.fading_out = True
            self.active = True

    def handle_fade_effect(self):
        if self.fading_out:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_out = False
                self.respawn_at_spawn()
                self.fading_in = True  # bắt đầu hiện lại

        elif self.fading_in:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_in = False

    def respawn_at_spawn(self):
        if self.world_ref:
            spawn_x, spawn_y = self.world_ref.player_start
            self.rect.topleft = (spawn_x, spawn_y)
            self.health = 1

    def activate(self):
        self.activated = True
        print("Checkpoint ready: Press ENTER to continue!")

    def update(self, player: "Player"):
        now = pygame.time.get_ticks()

        # --- animation loop ---
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        if self.level_id == 0:
            if self.active and not (self.fading_out or self.fading_in):
                if self.rect.colliderect(player.rect):
                    self.take_damage()
            self.handle_fade_effect()        
        
         # Level 1 → có hiệu ứng fade khi bị phá
        if self.level_id == 0:
            if self.active and not (self.fading_out or self.fading_in):
                if self.rect.colliderect(player.rect):
                    self.take_damage()
                    if not self.fading_out:  # khi checkpoint biến mất và respawn
                        self.win()  # Người chơi thắng

            self.handle_fade_effect()

        # Các level khác → checkpoint bình thường
        else:
            if self.rect.colliderect(player.rect) and not self.activated:
                if self.touch_time is None:
                    self.touch_time = now
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
        self.rect = pygame.Rect(x, y, 36, 46)
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
    def __init__(self, ascii_map, bg_path=None, level_id = 0):
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
                    self.checkpoints.append(Checkpoint(x, y,world_ref=self, level_id = level_id))
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
# HÀM CHẠY GAME CHÍNH
# ------------------------------
def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trap Adventure")
    clock = pygame.time.Clock()
    
    # Khởi tạo settings và game state
    settings = GameSettings()
    settings.apply_difficulty()
    game_state = GameState.MAIN_MENU
    
    # Khởi tạo game world (tạm thời)
    current_level_index = 0
    world = None
    
    # Khởi tạo HUD
    hud = HUD(None, settings)
    
    running = True
    
    def start_game():
        nonlocal world, current_level_index
        world = World(LEVELS[current_level_index], bg_path=LEVEL_BGS[current_level_index], level_id=current_level_index)
        hud.player = world.player
        return GameState.PLAYING

    while running:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Xử lý input cho menu
            if game_state in [GameState.MAIN_MENU, GameState.SETTINGS]:
                new_state = hud.handle_menu_input(event, game_state)
                if new_state == GameState.PLAYING and game_state == GameState.MAIN_MENU:
                    game_state = start_game()
                else:
                    game_state = new_state
            else:
                # Xử lý input trong game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game_state == GameState.PLAYING:
                            game_state = GameState.PAUSED
                        elif game_state == GameState.PAUSED:
                            game_state = GameState.PLAYING
                    elif event.key == pygame.K_m:  # Phím M để về menu
                        game_state = GameState.MAIN_MENU
        
        # UPDATE GAME
        if game_state == GameState.PLAYING and world:
            keys = pygame.key.get_pressed()
            world.update()
            
            player = world.player
            player.handle_input(keys)
            player.apply_gravity()
            player.move_and_collide(world.solids())
            
            # Xử lý checkpoint
            for cp in world.checkpoints:
                if cp.activated and keys[pygame.K_RETURN]:
                    current_level_index = (current_level_index + 1) % len(LEVELS)
                    world = World(LEVELS[current_level_index], bg_path=LEVEL_BGS[current_level_index])
                    hud.player = world.player
                    break
            
            # Update animation
            if player.health > 0:
                player.update_animation()
            else:
                player.update_death_animation()
                if player.dead and keys[pygame.K_r]:
                    world = World(LEVELS[current_level_index], bg_path=LEVEL_BGS[current_level_index])
                    hud.player = world.player
        
        # DRAW
        if game_state == GameState.PLAYING and world:
            world.draw_background(screen)
            world.draw(screen)
            hud.draw_ingame_hud(screen, current_level_index, len(LEVELS))
            
            # Vẽ pause text nếu đang pause
            if game_state == GameState.PAUSED:
                pause_text = hud.font.render("PAUSED - Press ESC to continue", True, (255, 255, 0))
                pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(pause_text, pause_rect)
        else:
            # Vẽ menu
            hud.draw_menu(screen, game_state)
        
        pygame.display.flip()

if __name__ == "__main__":
    run()
