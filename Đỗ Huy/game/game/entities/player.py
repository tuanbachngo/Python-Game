import pygame
from pygame import Rect
from ..core.constants import PLAYER_SPEED, GRAVITY, JUMP_VEL, MAX_FALL
from config import asset
from ..utlis.load import load_frames
# 1. Pre-init mixer trước pygame.init() để tránh lag
pygame.mixer.pre_init(44100, -16, 2, 512)  # 44.1kHz, 16bit, stereo, buffer nhỏ

class Player:
    def __init__(self, x, y, initial_health = 1):
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
        self.full_under_world = False
        self.swimming = False
        self.sit = False
        self.moved_by_platform = False

        self.health = initial_health
        self.ori_image = pygame.image.load(asset("mask_state.png")).convert_alpha()
        self.mask = pygame.mask.from_surface(self.ori_image)
        self.facing_right = True
        self.dead = False

        # --- Footstep sound ---
        self.snd_run = pygame.mixer.Sound(asset("walking_sound.mp3"))
        self.snd_run.set_volume(0.4)  # âm lượng chạy
        self.snd_jump = pygame.mixer.Sound(asset("jump_sound.mp3"))
        self.snd_jump.set_volume(0.5)  # âm lượng nhảy

        self._run_channel = pygame.mixer.Channel(1)  # channel riêng
        self._is_playing_run = False   
        self._jump_channel = pygame.mixer.Channel(2)  # channel riêng cho nhảy
        self._is_playing_jump = False

        # --- Animation frames ---
        self.animations = {
            "idle": load_frames(asset("idle-effect-sheet.png"), 48, 38, 9),
            "run": load_frames(asset("running-effect-sheet.png"), 48, 38, 4),
            "jump": load_frames(asset ("jumping-effect-sheet.png"), 48, 38, 3),
            "sit": load_frames(asset("sitting.png"), 48, 27, 4),
            "die": load_frames(asset("dying-effect-sheet.png"), 48, 48, 7),
            "swim_idle": load_frames(asset("swim_idle.png"), 48, 48, 4),
            "swimming": load_frames(asset("swimming.png"), 48, 48, 3),
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

        ax = 0
        if keys[pygame.K_LSHIFT] or keys[pygame.K_s] or keys[pygame.K_DOWN]and self.on_ground:
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
            if self.snd_jump:
                self._jump_channel.play(self.snd_jump)
                self._is_playing_jump = True
        
        if self.idle_underwater and (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            self.vel_y = -2
            self.swimming = True

        if self.idle_underwater and (keys[pygame.K_s] or keys[pygame.K_DOWN]):
            self.vel_y = 2
            self.swimming = True

    def apply_gravity(self):
        if self.idle_underwater:
            applied = GRAVITY * 0.2
            max_fall = MAX_FALL * 0.3
        else:
            applied = GRAVITY
            max_fall = MAX_FALL
        self.vel_y = min(self.vel_y + applied, max_fall)

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
        

    def update_state(self):
        # Cập nhật midbottom từ vị trí pos
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
        self.handle_run_sound()

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
            if self.dead and self._is_playing_run:
                self.snd_run.stop()
                self._is_playing_run = False

    def draw(self, surface, ox=0, oy=0):
        draw_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        surface.blit(self.image, (draw_rect.x + ox, draw_rect.y + oy))

    def handle_run_sound(self):
      #  """Phát hoặc dừng âm chạy tùy theo trạng thái"""
        if self.snd_run is None:
            return

        # Đang chạy + trên mặt đất
        if self.on_ground and abs(self.vel_x) > 0.2:
            if not self._is_playing_run:
                self.snd_run.play(-1)      # phát lặp
                self._is_playing_run = True
        else:
            if self._is_playing_run:
                self.snd_run.stop()        # dừng ngay lập tức
                self._is_playing_run = False
                
    def stop_running_sound(self):
    #"""Dừng âm chạy ngay lập tức và reset trạng thái"""
        if self._is_playing_run:
            self.snd_run.stop()
            self._is_playing_run = False