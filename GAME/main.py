import pygame
from pygame import Rect
from pathlib import Path
import sys
# ------------------------------
# CÀI ĐẶT CƠ BẢN
# ------------------------------
WIDTH, HEIGHT = 960, 480
FPS = 60
TILE = 48

GRAVITY = 0.32
MAX_FALL = 14
PLAYER_SPEED = 2
JUMP_VEL = 9

WHITE = (240, 240, 240)
BG = (20, 24, 28)
# ------------------------------
# HÀM TẢI ASSET 
# ------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

ASSETS_DIR = BASE_DIR / "pygame_assets"

def asset(name: str) -> str:
    return str(ASSETS_DIR / name)
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
        "#..................#",
        "#....M......L......#",
        "#.P................C",
        "###^^^^^^^^^^^^^^###",
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
        
    def get_max_levels(self):
        """Trả về số level tối đa cho độ khó"""
        if self.difficulty == "EASY":
            return 1
        elif self.difficulty == "NORMAL":
            return 2
        elif self.difficulty == "HARD":
            return 3
        return 1
    
    def get_player_health(self):
        """Trả về máu ban đầu cho player"""
        if self.difficulty == "EASY":
            return 5
        elif self.difficulty == "NORMAL":
            return 4
        elif self.difficulty == "HARD":
            return 3
        return 1
    
    def apply_difficulty(self, player=None):
        """Áp dụng độ khó cho game"""
        if player:
            player.health = self.get_player_health()
# ------------------------------
# CLASS MENU MANAGER
# ------------------------------
def render_center(surface, font, text, y, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)
    return rect
class MenuManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 32)
        self.font_small = pygame.font.SysFont("consolas", 20)
        
        # Màu sắc mới
        self.bg_color = (173, 216, 230)  # Baby Blue
        self.title_color = (0, 0, 0)     # Đen cho tiêu đề
        self.selected_color = (0, 0, 0)  # Đen cho option được chọn
        self.normal_color = (255, 255, 255)  # Trắng cho option bình thường
        self.highlight_color = (0, 100, 200)  # Xanh đậm để highlight độ khó hiện tại
        self.help_color = (80, 80, 80)   # Xám đậm cho text hướng dẫn
        
        self.main_menu_options = ["START GAME", "DIFFICULTY", "QUIT"]
        self.difficulty_options = ["EASY", "NORMAL", "HARD"]
        self.difficulty_descriptions = {
            "EASY": "1 Level, 5 Health",
            "NORMAL": "2 Levels, 4 Health", 
            "HARD": "3 Levels, 3 Health"
        }      
        self.selected_index = 0
        self.current_menu = "main"  
        self._item_rects = []

    def draw (self, surface, current_difficulty):
        surface.fill(self.bg_color)
        self._item_rects = []

        if self.current_menu == "main":
            render_center(surface, self.font_large, "TRAP ADVENTURE", 120, self.title_color)
            base_y = 250
            for i, label in enumerate(self.main_menu_options):
                color = self.selected_color if i == self.selected_index else self.normal_color
                rect = render_center(surface, self.font_medium, label, base_y + i * 70, color)
                self._item_rects.append(rect)
                if i == self.selected_index:
                    surface.blit(self.font_medium.render(">", True, self.selected_color),
                                    (rect.left - 40, rect.y))
        else:
            render_center(surface, self.font_medium, "SELECT DIFFICULTY", 100, self.title_color)
            base_y = 200
            for i, label in enumerate(self.difficulty_options):
                if i == self.selected_index:
                    color = self.selected_color
                elif label == current_difficulty:
                    color = self.highlight_color  # độ khó đang áp dụng
                else:
                    color = self.normal_color

                rect = render_center(surface, self.font_medium, label, base_y + i * 80, color)
                self._item_rects.append(rect)
                render_center(surface, self.font_small, self.difficulty_descriptions[label],
                                    rect.centery + 30, self.help_color)
                if i == self.selected_index:
                    surface.blit(self.font_medium.render(">>", True, self.selected_color),
                                        (rect.left - 60, rect.y))

            render_center(surface, self.font_small, "ENTER: Select  |  ESC: Back",
                                self.screen_height - 50, self.help_color)
                
    def handle_mouse_hover(self, mouse_pos):
        """Highlight option khi di chuột qua"""
        if self.current_menu == "main":
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break
        else:  # difficulty menu
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break

    def handle_main_menu_mouse(self, mouse_pos, settings):
        """Xử lý click chuột trên main menu"""
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                
                option = self.main_menu_options[i]
                if option == "START GAME":
                    return "start_game"
                elif option == "DIFFICULTY":
                    self.current_menu = "difficulty"
                    self.selected_index = self.difficulty_options.index(settings.difficulty)
                elif option == "QUIT":
                    return "quit"
        return None

    def handle_difficulty_mouse(self, mouse_pos, settings):
        """Xử lý click chuột trên difficulty menu"""
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                settings.difficulty = self.difficulty_options[i]
                settings.apply_difficulty()
                self.current_menu = "main"
                self.selected_index = 1
                return None
        return None

    def handle_input(self, event, settings):
        """Xử lý cả bàn phím và chuột"""
        # Xử lý hover chuột
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event.pos)
        
        # Xử lý click chuột
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click trái
            if self.current_menu == "main":
                return self.handle_main_menu_mouse(event.pos, settings)
            else:
                return self.handle_difficulty_mouse(event.pos, settings)
        
        # Xử lý bàn phím
        if event.type == pygame.KEYDOWN:
            if self.current_menu == "main":
                return self.handle_main_menu_input(event, settings)
            else:
                return self.handle_difficulty_input(event, settings)
        return None

    def handle_main_menu_input(self, event, settings):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.main_menu_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.main_menu_options)
        elif event.key == pygame.K_RETURN:
            selected_option = self.main_menu_options[self.selected_index]
            
            if selected_option == "START GAME":
                return "start_game"
            elif selected_option == "DIFFICULTY":
                self.current_menu = "difficulty"
                self.selected_index = self.difficulty_options.index(settings.difficulty)
            elif selected_option == "QUIT":
                return "quit"
                
        elif event.key == pygame.K_ESCAPE:
            return "quit"
            
        return None

    def handle_difficulty_input(self, event, settings):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.difficulty_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.difficulty_options)
        elif event.key == pygame.K_RETURN:
            settings.difficulty = self.difficulty_options[self.selected_index]
            settings.apply_difficulty()
            self.current_menu = "main"
            self.selected_index = 1  # Quay lại mục Difficulty trong menu chính
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
            self.selected_index = 1  # Quay lại mục Difficulty trong menu chính
        return None
# ------------------------------
# CLASS HUD
# ------------------------------
class HUD:
    def __init__(self, player, settings):
        self.player = player
        self.settings = settings
        self.font = pygame.font.SysFont("consolas", 20)
        
        # Menu manager
        self.menu_manager = MenuManager(WIDTH, HEIGHT)
    
    def draw_ingame_hud(self, surface, current_level, total_levels):
        # Tạo chuỗi thông tin trên 1 dòng
        info_text = f"Health: {self.player.health} | Level: {current_level + 1}/{total_levels} | Difficulty: {self.settings.difficulty}"

        text_surf = self.font.render(info_text, True, (0, 0, 0))  
        
        # Vẽ background cho HUD (cách viền 60px cả trên và trái)
        bg_x = 60  # Cách trái 60px
        bg_y = 60  # Cách trên 60px
        bg_rect = pygame.Rect(bg_x, bg_y, text_surf.get_width() + 20, text_surf.get_height() + 10)
        pygame.draw.rect(surface, (255, 255, 255, 180), bg_rect)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 2) 
        
        text_x = bg_x + 10 
        text_y = bg_y + 5   
        surface.blit(text_surf, (text_x, text_y))
    
    def draw_menu(self, surface):
        self.menu_manager.draw(surface, self.settings.difficulty)
    
    def handle_menu_input(self, event):
        return self.menu_manager.handle_input(event, self.settings)
# ------------------------------
# CLASS PLAYER
# ------------------------------
class Player:
    def __init__(self, x, y, initial_health=1):
        self.rect = Rect(x, y, 36 , 46)
        self.vel_x = 0
        self.vel_y = 0
        self.pos = pygame.Vector2(x, y)
        self.on_ground = False
        self.health = initial_health
        self.ori_image = pygame.image.load(asset("mask_state.png")).convert_alpha()
        self.mask = pygame.mask.from_surface(self.ori_image)
        self.facing_right = True
        self.dead = False
        self.moved_by_platform = False

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
        # Reset flag
        self.moved_by_platform = False
        self.on_ground = False
        prev_rect = self.rect.copy()
        
        # ---- DI CHUYỂN NGANG (X) ----
        self.rect.x += float(self.vel_x)
        
        # CHỈ kiểm tra va chạm ngang nếu KHÔNG được platform di chuyển
        if not self.moved_by_platform:
            for s in solids:
                if self.rect.colliderect(s.rect):
                    if self.vel_x > 0:  # va phải
                        self.rect.right = s.rect.left
                    elif self.vel_x < 0:  # va trái
                        self.rect.left = s.rect.right

        # ---- DI CHUYỂN DỌC (Y) ----
        self.rect.y += float(self.vel_y)
        moving_platform = None
        
        for s in solids:
            if self.rect.colliderect(s.rect):
                # Rơi xuống và chạm mặt đất
                if prev_rect.bottom <= s.rect.top and self.vel_y >= 0:
                    self.rect.bottom = s.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    
                    # KIỂM TRA CÓ PHẢI MOVING PLATFORM KHÔNG
                    if hasattr(s, 'get_velocity'):
                        moving_platform = s
                        
                # Nhảy lên và đụng trần
                elif prev_rect.top >= s.rect.bottom and self.vel_y <= 0:
                    self.rect.top = s.rect.bottom
                    self.vel_y = 0

        # ---- XỬ LÝ MOVING PLATFORM SAU KHI DI CHUYỂN ----
        if moving_platform and self.on_ground:
            vel = moving_platform.get_velocity()
            # CHỈ di chuyển player nếu platform thực sự di chuyển
            if abs(vel.x) > 0 or abs(vel.y) > 0:
                # ĐÁNH DẤU player đang được platform di chuyển
                self.moved_by_platform = True
                self.rect.x += float(vel.x)
                self.rect.y += float(vel.y)

        # ---- KIỂM TRA NỀN DƯỚI CHÂN ----
        if not self.on_ground:
            check_distance = min(int(self.vel_y + GRAVITY) + 2, 10)
            for s in solids:
                if s.rect.colliderect(self.rect.move(0, check_distance)):
                    self.on_ground = True
                    break
        
        # Cập nhật vector vị trí từ rect
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
# ------------------------------
class MovingPlatform(Block):
    def __init__(self, x, y, dx=2, dy=0, move_range=100, world_ref=None):
        super().__init__(x, y)
        self.start_x = x
        self.start_y = y
        self.dx = dx
        self.dy = dy
        self.move_range = move_range
        self.direction = 1
        self.prev_pos = pygame.Vector2(self.rect.x, self.rect.y)
        self.world_ref = world_ref
        self.current_velocity = pygame.Vector2(0, 0)
        # THÊM: lưu vận tốc dự kiến cho frame tiếp theo
        self.next_velocity = pygame.Vector2(dx * self.direction, dy * self.direction)
    
    def update(self):
        # Lưu vị trí cũ
        self.prev_pos.update(self.rect.x, self.rect.y)
        old_x, old_y = self.rect.x, self.rect.y

        # Tính toán vận tốc cho frame NÀY
        self.next_velocity = pygame.Vector2(
            self.dx * self.direction, 
            self.dy * self.direction
        )
        
        # Di chuyển
        self.rect.x += self.next_velocity.x
        self.rect.y += self.next_velocity.y

        # Kiểm tra va chạm
        if self.world_ref and self.check_collision_with_blocks():
            self.rect.x, self.rect.y = old_x, old_y
            self.direction *= -1
            # Cập nhật lại vận tốc sau khi đổi hướng
            self.next_velocity = pygame.Vector2(
                self.dx * self.direction, 
                self.dy * self.direction
            )
        elif abs(self.rect.x - self.start_x) >= self.move_range or abs(self.rect.y - self.start_y) >= self.move_range:
            self.direction *= -1
            self.next_velocity = pygame.Vector2(
                self.dx * self.direction, 
                self.dy * self.direction
            )

        # Tính vận tốc thực tế
        self.current_velocity.x = self.rect.x - self.prev_pos.x
        self.current_velocity.y = self.rect.y - self.prev_pos.y

    def get_velocity(self):
        # Trả về vận tốc sẽ di chuyển trong frame TIẾP THEO
        return self.next_velocity 
# ------------------------------
# CLASS WORLD
# ------------------------------
class World:
    def __init__(self, ascii_map, bg_path=None, level_id = 0, player_health=1):
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
                    self.blocks.append(MovingPlatform(x,y,dx=2,dy=0,move_range=150))
                elif ch == 'L':
                    self.blocks.append(MovingPlatform(x,y,dx=-2,dy=0,move_range=150))
                elif ch == 'H':
                    self.spikes.append(HiddenSpike(x, y))   
        self.player = Player(*self.player_start, initial_health=player_health)

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
    
    # Khởi tạo
    settings = GameSettings()
    
    game_state = "menu"  # "menu", "playing"
    current_level_index = 0
    world = None   
    hud = HUD(None, settings)
    running = True
    
    def restart_game():
        nonlocal world, current_level_index
        player_health = settings.get_player_health()
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player

    def start_new_game():
        nonlocal world, current_level_index
        current_level_index = 0
        player_health = settings.get_player_health()
        world = World(
            LEVELS[current_level_index], 
            bg_path=LEVEL_BGS[current_level_index], 
            level_id=current_level_index,
            player_health=player_health
        )
        hud.player = world.player
        print(f"Starting game - Difficulty: {settings.difficulty}, Health: {player_health}")  # Debug

    while running:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "menu":
                result = hud.handle_menu_input(event)
                if result == "start_game":
                    start_new_game()
                    game_state = "playing"
                elif result == "quit":
                    running = False
            elif game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"  # ESC để về menu
                    elif event.key == pygame.K_r and world.player.dead:
                        restart_game()
        
        # Gameplay
        if game_state == "playing" and world:
            keys = pygame.key.get_pressed()

            world.player.handle_input(keys)
            world.player.apply_gravity()
            world.player.move_and_collide(world.solids())
            world.update()

            # Xử lý checkpoint - CHỈ cho phép chuyển level nếu chưa vượt quá số level cho phép
            max_levels = settings.get_max_levels()
            for cp in world.checkpoints:
                if cp.activated and keys[pygame.K_RETURN]:
                    if current_level_index < max_levels - 1:  # Chưa đạt level cuối
                        current_level_index += 1
                        player_health = world.player.health  # Giữ nguyên máu hiện tại
                        world = World(
                            LEVELS[current_level_index], 
                            bg_path=LEVEL_BGS[current_level_index],
                            level_id=current_level_index,
                            player_health=player_health
                        )
                        hud.player = world.player
                        print(f"Advanced to Level {current_level_index + 1}")
                    else:
                        # Đã hoàn thành tất cả level
                        print("Game Completed!")
                        game_state = "menu"
                    break
            
            # Update animation
            if world.player.health > 0:
                world.player.update_animation()
            else:
                world.player.update_death_animation()
        
        # Drawing
        screen.fill((0, 0, 0))
        
        if game_state == "playing" and world:
            world.draw_background(screen)
            world.draw(screen)
            hud.draw_ingame_hud(screen, current_level_index, len(LEVELS))

            if world.player.dead:
                death_text = hud.font.render("YOU DIED! Press R to restart", True, (255, 50, 50))
                death_rect = death_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(death_text, death_rect)
        else:
            hud.draw_menu(screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    run()
