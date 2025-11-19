import pygame
from pygame import Rect
from ..utlis.load import load_frames
from config import asset
from ..entities.player import Player
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
    def __init__(self, x, y, image_path = "block.png"):
        self.rect = pygame.Rect(x, y, 36, 46)
        self.image = pygame.image.load(asset(image_path)).convert_alpha()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS PLATFORM
# ------------------------------
class MovingPlatform(Block):
    def __init__(self, x, y, dx=2, dy=0, move_range=100, world_ref=None):
        super().__init__(x, y, "platform.png")
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