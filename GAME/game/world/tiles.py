import pygame
from pygame import Rect
from ..utlis.load import load_frames
from ..core.constants import WIDTH, TILE
from config import asset
from ..entities.player import Player
import math
import random
# ------------------------------
# CLASS SPIKE
# ------------------------------
class Spike:
    def __init__(self, x, y, direction="UP"):
        self.rect = Rect(x, y, 36, 36)

        # Animation
        self.frames = load_frames(asset("trap-1-sheet.png"), 48, 48, 2)
        self.frame_index = 0
        self.frame_speed = 0.15

        # Hướng spike
        self.direction = direction.upper()

        # Xoay frame đầu tiên theo hướng
        self.image = self._rotate(self.frames[int(self.frame_index)])

    def _rotate(self, image):
        """Xoay spike theo hướng mong muốn."""
        if self.direction == "UP":
            return image
        elif self.direction == "DOWN":
            return pygame.transform.rotate(image, 180)
        elif self.direction == "LEFT":
            return pygame.transform.rotate(image, 90)
        elif self.direction == "RIGHT":
            return pygame.transform.rotate(image, -90)
        return image

    def update(self, player: Player):
        # Animation
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        # Update frame xoay theo hướng
        raw_frame = self.frames[int(self.frame_index)]
        self.image = self._rotate(raw_frame)

        # Va chạm
        if self.rect.colliderect(player.rect):
            if player.health > 0:
                player.health -= 1
            player.vel_y = -8  # knockback

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
# ------------------------------
class HiddenSpike(Spike):
    """Bẫy ẩn: ban đầu vô hình, khi player chạm thì hiện hình và gây chết ngay."""
    def __init__(self, x, y, delay = 0):
        super().__init__(x, y,direction="UP")
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
        self.sound_played = False

    def update(self, player: "Player"):
        # Animation frame
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
        # Kiểm tra va chạm
        if not self.activated and self.rect.colliderect(player.rect):
            self.activated = True
            if self.activated and not self.sound_played:
                self.sound_played = True

    def draw(self, surface, ox=0,oy=0):
        surface.blit(self.image, (self.rect.x+ox, self.rect.y+oy))
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
    
    def draw(self, surface,ox=0,oy=0):
        if self.active :
            if self.fading:
                self.image.set_alpha(self.fade_alpha)
            surface.blit(self.image, (self.rect.x+ox, self.rect.y+oy))
# ------------------------------
class DelayCheckpoint(Checkpoint):
    def __init__(self, x, y, world_ref=None):
        super().__init__(x, y, world_ref)
        self.delay = 15000
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

    def draw(self, surface,ox=0,oy=0):
        if self.exists:
            surface.blit(self.image, (self.rect.x+ox, self.rect.y+oy))
#-------------------------------
class LevelGate(Checkpoint):
    def __init__(self, x, y, world_ref = None):
        super().__init__(x,y,world_ref)
        self.rect = pygame.Rect(x, y, 48, 48)  
        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        self.mask = pygame.mask.from_surface(self.image)
        self.activated = False

    def update(self, player: "Player"):
        if not self.activated and self.rect.colliderect(player.rect):
            self.activated = True
# ------------------------------
# CLASS BLOCK
# ------------------------------
class Block:
    def __init__(self, x, y, image_path = "block.png"):
        self.rect = pygame.Rect(x, y, 36, 46)
        self.image = pygame.image.load(asset(image_path)).convert_alpha()

    def draw(self, surface, ox=0, oy=0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
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
# ------------------------------
# CLASS BUBBLE
# ------------------------------
class Bubble:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 2  # tốc độ cố định
        self.image = pygame.image.load(asset("bubble.png")).convert_alpha()
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
# CLASS ARROW
# ------------------------------
class ArrowTrap:
    def __init__(self, x, y):
        self.x = x
        self.y = y  # vị trí gốc (đỉnh arrow khi rút xuống)
        self.width = 48
        self.max_height = 560  # chiều cao tối đa mũi tên khi đâm lên

        # Load ảnh arrow
        self.image = pygame.image.load(asset("arrow.png")).convert_alpha()
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
# CLASS TIDE
# ------------------------------
class Tide:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.frames = load_frames(asset("tide.png"), 48, 48, 3)
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
class Water:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image = pygame.image.load(asset("water.png")).convert_alpha()
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
class BubbleSpout:
    def __init__(self, x, y):
        # 6 frame, mỗi frame 96x48, giống main3
        self.frames = load_frames(asset("fish_bubble.png"), 96, 48, 7)
        self.frame_index = 0
        self.anim_speed = 0.035
        self.anim_timer = 0.0

        self.image = self.frames[self.frame_index]
        self.rect = pygame.Rect(x, y, 96, 27)

        # những frame đang phun bong bóng
        self.spray_frames = {2, 3}
        self.is_spraying = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.mask = pygame.mask.from_surface(self.image)

        self.is_spraying = self.frame_index in self.spray_frames

    def draw(self, surface, ox=0, oy=0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))

    def check_collision_and_knockback(self, player):
        if not self.is_spraying:
            return
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset):
            # đẩy player sang phải, cậu có thể chỉnh lực
            player.rect.x += 5
            # đồng bộ lại pos nếu cậu dùng self.pos
            if hasattr(player, "pos"):
                player.pos.x = player.rect.centerx
class Switch:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.image_off = pygame.image.load(asset("unactivated_switch.png")).convert_alpha()
        self.image_on  = pygame.image.load(asset("activated_switch.png")).convert_alpha()
        self.image = self.image_off
        self.mask = pygame.mask.from_surface(self.image)
        self.activated = False

    def update(self, player, world=None):
        if self.activated:
            # đã bật thì giữ sprite ON, không cần check thêm
            self.image = self.image_on
            self.mask = pygame.mask.from_surface(self.image)
            return

        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        switch_mask = pygame.mask.from_surface(self.image)
        if switch_mask.overlap(player.mask, offset):
            self.activated = True
            self.image = self.image_on
            self.mask = pygame.mask.from_surface(self.image)
            # cơ chế chính: bật trọng lực trong nước
            player.gravity_effect_active = True

    def draw(self, surface, ox=0, oy=0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))
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
        self.rotate_image = pygame.image.load(asset("full_moving_wall.png")).convert_alpha()
        self.original_image = pygame.image.load(asset( "only_wall.png")).convert_alpha()
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
class SimpleMovingWall:
    def __init__(self, x, y):
        self.width = 67
        self.height = 144
        self.rect = pygame.Rect(x-70, y-96, self.width, self.height)
        # dùng asset only_wall
        self.image = pygame.image.load(asset("only_wall_flipped.png")).convert_alpha()
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
        self.image = pygame.image.load(asset("connected_block.png")).convert_alpha()

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

        self.image = pygame.image.load(asset("stone.png")).convert_alpha()
        mask_img = pygame.image.load(asset("stonemask.png")).convert_alpha()
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
        self.rect = pygame.Rect(x, y+36, 48, 24)
        self.image = pygame.image.load(asset("half_block.png")).convert_alpha()

    def draw(self, surface, ox = 0, oy = 0):
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))

# ------------------------------
# CLASS WALL
# ------------------------------
class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 19)
        self.image = pygame.image.load(asset("wall.png")).convert_alpha()

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
