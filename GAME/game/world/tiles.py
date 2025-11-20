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
        self.frames = load_frames(asset("trap-1-sheet.png"), 48, 48, 2)
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = self.frames[int(self.frame_index)]

    def update(self, player: Player):
        # Animation frame
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        # Kiểm tra va chạm
        if self.rect.colliderect(player.rect):
                player.health -= 1 if player.health > 0 else 0
                player.vel_y = -8 

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
class HiddenSpike(Spike):
    """Bẫy ẩn: ban đầu vô hình, khi player chạm thì hiện hình và gây chết ngay."""
    def __init__(self, x, y, delay = 0):
        super().__init__(x, y)
        self.active = False          # ban đầu ẩn
        self.delay = delay
        self.start_time = pygame.time.get_ticks()

    def update(self, player: "Player"):
        if not self.active and pygame.time.get_ticks() - self.start_time >= self.delay:
            self.active = True
        
        if self.active and self.rect.colliderect(player.rect):
            player.health = 0
            player.vel_y = -12

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS CHECKPOINT
# ------------------------------
class Checkpoint:
    def __init__(self, x, y, world_ref = None):
        self.rect = Rect(x, y, 48, 48)
        self.frames = load_frames(asset("activated-checkpoint-sheet.png"), 48, 48, 3)
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = self.frames[int(self.frame_index)]
        self.activated = False
        self.world_ref = world_ref

    def update(self, player: "Player"):
        # Animation frame
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
        # Kiểm tra va chạm
        if not self.activated and self.rect.colliderect(player.rect):
            self.activated = True

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
# CLASS FAKE CHECKPOINT 
# ------------------------------
class FakeCheckpoint(Checkpoint):
    def __init__(self, x, y, world_ref=None):
        super().__init__(x, y, world_ref)
        self.active = True
        
        # Hiệu ứng biến mất
        self.fade_alpha = 150
        self.fading = False
    
    def update(self, player: "Player"):
        # Animation frame
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
        # Hiệu ứng fade
        if self.fading:
            self.fade_alpha -= 10
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.active  = False
        
        # Kiểm tra va chạm
        if self.active  and not self.fading and self.rect.colliderect(player.rect):
            self.fading = True
    
    def draw(self, surface):
        if self.active :
            if self.fading:
                self.image.set_alpha(self.fade_alpha)
            surface.blit(self.image, (self.rect.x, self.rect.y))

# ------------------------------
# CLASS DELAY CHECKPOINT
# ------------------------------
class DelayCheckpoint(Checkpoint):
    def __init__(self, x, y, world_ref=None):
        super().__init__(x, y, world_ref)
        self.delay = 15400
        self.start_time = pygame.time.get_ticks()
        self.exists = False 
    
    def update(self, player: "Player"):
        # Kiểm tra thời gian xuất hiện
        if not self.exists and pygame.time.get_ticks() - self.start_time >= self.delay:
            self.exists = True
        
        if self.exists:
            self.frame_index += self.frame_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

            if not self.activated and self.rect.colliderect(player.rect):
                self.activated = True

    def draw(self, surface):
        if self.exists:
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
