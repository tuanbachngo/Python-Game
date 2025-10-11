# Trap-Adventure-like (from scratch)
# Single-file starter you can copy to main.py and run.
# Made for teaching: clean, commented, and easy to extend.
# Requires: Python 3.10+ and pygame (pip install pygame)
# Thêm: tạo thêm 2 levels, tạo ra quái vật, vẽ nhân vật, quái, tạo checkpoint để qua level, tạo thêm loại bẫy --> vẽ sau
# Tuần 2: tạo folder code class, code và hiểu cách tạo nhân vật và world, hiểu vật lí của game
# Tuần 3: code input player (điều khiển tương tác nhân vật), tạo collision, tạo level
# Tuần 4: Add nhạc(tùy chọn), Menu, HUD, Debug, merge code
import sys
import math
import pygame
from pygame import Rect
import os

ASSETS = {}

def load_image(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    return img

def try_load(path, scale=None):
    return load_image(path, scale) if os.path.exists(path) else None

def load_assets():
    base = "assets"
    a = {}
    # Tiles
    a["tile_block"]    = try_load(os.path.join(base, "tiles", "block.png"), (TILE, TILE))
    a["tile_platform"] = try_load(os.path.join(base, "tiles", "platform.png"), (TILE, TILE))
    a["tile_spike_up"] = try_load(os.path.join(base, "tiles", "spike_up.png"), (TILE, TILE))
    # Props
    a["goal"] = try_load(os.path.join(base, "props", "door.png"), (TILE, TILE))
    # Background (tuỳ chọn)
    a["bg_sky"]   = try_load(os.path.join(base, "bg", "bg_sky.png"), (WIDTH, HEIGHT))
    a["bg_hills"] = try_load(os.path.join(base, "bg", "bg_hills.png"))  # để parallax, không scale
    # Player frames
    a["player_idle"] = [p for p in [try_load(os.path.join(base, "player", "idle_0.png"))] if p]
    a["player_run"]  = [img for i in range(4)
                        if (img := try_load(os.path.join(base, "player", f"run_{i}.png")))]
    return a

# ------------------------------
# CÀI ĐẶT CƠ BẢN
# ------------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

# Vật lý đơn giản
GRAVITY = 0.6
MAX_FALL = 14
PLAYER_SPEED = 4.2
JUMP_VEL = -12
COYOTE_MS = 120  # nhảy "cứu cánh" sau khi rời đất ~0.12s

# Màu sắc
BG = (20, 24, 28)
WHITE = (240, 240, 240)
GREY = (120, 128, 140)
GREEN = (80, 200, 120)
RED = (220, 60, 80)
YELLOW = (250, 210, 90)
CYAN = (100, 210, 230)
BROWN = (120, 90, 60)
ORANGE = (240, 150, 60)

# ------------------------------
# BẢN ĐỒ ASCII (có thể chỉnh sửa dễ dàng)
# Ký hiệu:
#   # : khối đất/đá rắn (solid)
#   . : khoảng trống
#   P : vị trí người chơi bắt đầu
#   G : đích/goal
#   ^ : gai luôn hoạt động (chạm là chết)
#   T : bẫy kích hoạt ẩn (đi vào mới bật gai sau 0.25s)
#   F : nền rơi (đứng lên một lúc sẽ rơi)
# ------------------------------
LEVEL_MAP = [
    "########################",  # 24 cột => 24 * 48 = 1152px (có cuộn màn hình)
    "#......................#",
    "#...............T......#",
    "#......................#",
    "#..P.........#####.....#",
    "#............#...#.....#",
    "#......F.....#...#..G..#",
    "#............#...#.....#",
    "#............#...#..^..#",
    "#......................#",
    "########################",
]
# ------------------------------
# HỖ TRỢ VẼ
# ------------------------------
def draw_block(surface, rect, offset_x):
    r = Rect(rect.x - offset_x, rect.y, rect.w, rect.h)
    img = ASSETS.get("tile_block")
    if img:
        surface.blit(img, r.topleft)
    else:
        pygame.draw.rect(surface, (120, 90, 60), r)
        pygame.draw.rect(surface, (0, 0, 0), r, 2)

def draw_platform(surface, rect, offset_x):
    r = Rect(rect.x - offset_x, rect.y, rect.w, rect.h)
    img = ASSETS.get("tile_platform")
    if img:
        surface.blit(img, r.topleft)
    else:
        pygame.draw.rect(surface, (150, 120, 90), r)
        pygame.draw.line(surface, (0, 0, 0), (r.left, r.top), (r.right, r.top), 2)
        pygame.draw.rect(surface, (0, 0, 0), r, 2)

def draw_spike_up(surface, rect, offset_x, active: bool):
    r = Rect(rect.x - offset_x, rect.y - TILE//2, TILE, TILE)  # hình ảnh full tile
    img = ASSETS.get("tile_spike_up")
    if img:
        surface.blit(img, r.topleft)
    else:
        # fallback tam giác
        x1, y1 = r.left, r.bottom
        x2, y2 = r.centerx, r.top
        x3, y3 = r.right, r.bottom
        color = RED if active else GREY
        pygame.draw.polygon(surface, color, [(x1, y1), (x2, y2), (x3, y3)])
        pygame.draw.polygon(surface, (0, 0, 0), [(x1, y1), (x2, y2), (x3, y3)], 2)

def draw_goal(surface, rect, offset_x):
    r = Rect(rect.x - offset_x, rect.y, rect.w, rect.h)
    img = ASSETS.get("goal")
    if img:
        surface.blit(img, r.topleft)
    else:
        r2 = Rect(r.x + 6, r.y + 6, r.w - 12, r.h - 12)
        pygame.draw.rect(surface, (60, 80, 160), r2, border_radius=6)
        pygame.draw.rect(surface, (20, 30, 80), r2, 3, border_radius=6)
        knob = Rect(r2.right - 16, r2.centery - 4, 8, 8)
        pygame.draw.rect(surface, YELLOW, knob, border_radius=4)

def draw(self, surface, offset_x):
    frames = None
    if ASSETS.get("player_run") and abs(self.vel_x) > 0.15:
        frames = ASSETS["player_run"]
    elif ASSETS.get("player_idle"):
        frames = ASSETS["player_idle"]

    if frames:
        now = pygame.time.get_ticks()
        idx = (now // 120) % len(frames)
        img = frames[idx]
        if self.vel_x < -0.1:
            img = pygame.transform.flip(img, True, False)
        # căn CHÂN vào đáy rect
        x = self.rect.centerx - img.get_width() // 2 - offset_x
        y = self.rect.bottom - img.get_height()
        surface.blit(img, (x, y))
    else:
        # fallback khối màu
        r = Rect(self.rect.x - offset_x, self.rect.y, self.rect.w, self.rect.h)
        pygame.draw.rect(surface, CYAN, r, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), r, 2, border_radius=6)
# ------------------------------
# THỰC THỂ TRÒ CHƠI
# ------------------------------
class Spike:
    """Gai hướng lên. Dùng rect mỏng để va chạm công bằng hơn."""

    def __init__(self, x, y, active_after_ms=0):
        self.rect = Rect(x, y + TILE // 2, TILE, TILE // 2)
        self.activate_at = pygame.time.get_ticks() + active_after_ms

    def is_active(self, now_ms):
        return now_ms >= self.activate_at


class Trigger:
    """Ô kích hoạt ẩn. Khi chạm sẽ gọi callback tạo bẫy."""

    def __init__(self, x, y, on_trigger):
        self.rect = Rect(x, y, TILE, TILE)
        self.on_trigger = on_trigger
        self.triggered = False

    def try_trigger(self, player_rect, now_ms):
        if (not self.triggered) and self.rect.colliderect(player_rect):
            self.triggered = True
            self.on_trigger(now_ms)


class FallingPlatform:
    def __init__(self, x, y):
        self.rect = Rect(x, y, TILE, TILE)
        self.falling = False
        self.vel_y = 0
        self._armed_time = None
        self.delay_ms = 250  # chạm ~0.25s rồi mới rơi

    def arm_if_player_on_top(self, player_rect, now_ms):
        if self.falling:
            return
        # Người chơi đứng trên (tiếp xúc cạnh trên) và chồng ngang > 8px
        on_top = (
            player_rect.bottom <= self.rect.top + 2
            and player_rect.bottom >= self.rect.top - 6
            and player_rect.right - 8 > self.rect.left
            and player_rect.left + 8 < self.rect.right
        )
        if on_top and self._armed_time is None:
            self._armed_time = now_ms

    def update(self, now_ms):
        if self.falling:
            self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
            self.rect.y += int(self.vel_y)
        elif self._armed_time is not None and now_ms - self._armed_time >= self.delay_ms:
            self.falling = True


class Player:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 28, 38)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.coyote_ms = 0
        self._jump_was_down = False

    def handle_input(self, keys):
        ax = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += 1
        self.vel_x = ax * PLAYER_SPEED

    def try_jump(self, jump_down, now_ms):
        if jump_down and not self._jump_was_down:
            if self.on_ground or self.coyote_ms > 0:
                self.vel_y = JUMP_VEL
                self.on_ground = False
                self.coyote_ms = 0
        self._jump_was_down = jump_down

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)

    def move_and_collide(self, solids):
        # --- ngang ---
        self.rect.x += int(self.vel_x)
        for s in solids:
            if self.rect.colliderect(s):
                if self.vel_x > 0:
                    self.rect.right = s.left
                elif self.vel_x < 0:
                    self.rect.left = s.right
        # --- dọc ---
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for s in solids:
            if self.rect.colliderect(s):
                if self.vel_y > 0:
                    self.rect.bottom = s.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = s.bottom
                    self.vel_y = 0
        # coyote
        if self.on_ground:
            self.coyote_ms = COYOTE_MS
        else:
            self.coyote_ms = max(0, self.coyote_ms - (1000 // FPS))

# ------------------------------
# XÂY DỰNG LEVEL TỪ ASCII
# ------------------------------
class World:
    def __init__(self, ascii_map):
        self.blocks: list[Rect] = []
        self.spikes: list[Spike] = []
        self.triggers: list[Trigger] = []
        self.platforms: list[FallingPlatform] = []
        self.goal: Rect | None = None
        self.player_start = (64, 64)

        for j, row in enumerate(ascii_map):
            for i, ch in enumerate(row):
                x, y = i * TILE, j * TILE
                if ch == '#':
                    self.blocks.append(Rect(x, y, TILE, TILE))
                elif ch == '^':
                    self.spikes.append(Spike(x, y, active_after_ms=0))
                elif ch == 'T':
                    # Khi kích hoạt: bật một hàng gai tại vị trí này sau 250ms
                    def _on_trigger(now_ms, rx=x, ry=y):
                        self.spikes.append(Spike(rx, ry, active_after_ms=250))
                    self.triggers.append(Trigger(x, y, _on_trigger))
                elif ch == 'F':
                    self.platforms.append(FallingPlatform(x, y))
                elif ch == 'G':
                    self.goal = Rect(x, y, TILE, TILE)
                elif ch == 'P':
                    # đặt người chơi trên sàn (trung bình cell)
                    self.player_start = (x + TILE // 2 - 14, y + TILE // 2)

        self.level_px_w = len(ascii_map[0]) * TILE
        self.level_px_h = len(ascii_map) * TILE

    def solids(self):
        # khối + platform chưa rơi
        sols = list(self.blocks)
        sols.extend([p.rect for p in self.platforms if not p.falling])
        return sols


# ------------------------------
# VÒNG LẶP CHÍNH
# ------------------------------
STATE_PLAY, STATE_DEAD, STATE_WON = 0, 1, 2


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    global ASSETS
    ASSETS = load_assets()
    pygame.display.set_caption("Trap-Adventure-like — Starter")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    big_font = pygame.font.SysFont("consolas", 48)

    world = World(LEVEL_MAP)
    player = Player(*world.player_start)

    state = STATE_PLAY
    death_reason = ""
    debug = False
    camera_x = 0

    def restart():
        nonlocal world, player, state, death_reason, camera_x
        world = World(LEVEL_MAP)
        player = Player(*world.player_start)
        state = STATE_PLAY
        death_reason = ""
        camera_x = 0

    while True:
        dt_ms = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F1:
                    debug = not debug
                if e.key == pygame.K_r:
                    restart()

        keys = pygame.key.get_pressed()
        jump_down = keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]

        if state == STATE_PLAY:
            # điều khiển
            player.handle_input(keys)
            player.try_jump(jump_down, now)
            player.apply_gravity()

            # platform arming (trước khi collide dọc xong ta sẽ set chính xác)
            for p in world.platforms:
                p.arm_if_player_on_top(player.rect, now)
                p.update(now)

            # va chạm
            player.move_and_collide(world.solids())

            # camera
            camera_x = max(0, min(player.rect.centerx - WIDTH // 2, world.level_px_w - WIDTH))

            # triggers
            for t in world.triggers:
                t.try_trigger(player.rect, now)

            # chết vì gai
            for sp in world.spikes:
                if sp.is_active(now) and player.rect.colliderect(sp.rect):
                    state = STATE_DEAD
                    death_reason = "Bạn dẫm vào gai!"
                    break

            # rơi khỏi map
            if player.rect.top > world.level_px_h + 200:
                state = STATE_DEAD
                death_reason = "Bạn rơi xuống vực!"

            # thắng
            if world.goal and player.rect.colliderect(world.goal):
                state = STATE_WON

        # ---------------- DRAW ----------------
        screen.fill(BG)

        # nền xa (ưu tiên ảnh)
        bg_sky = ASSETS.get("bg_sky")
        if bg_sky:
            screen.blit(bg_sky, (0, 0))
        else:
        # fallback
            parallax = int(camera_x * 0.2)
        for i in range(0, WIDTH + 200, 200):
            pygame.draw.circle(screen, (30, 34, 40), (i - parallax, 120), 90, 2)

        bg_hills = ASSETS.get("bg_hills")
        if bg_hills:
        # lặp ảnh theo chiều ngang với parallax nhẹ
            parallax = int(camera_x * 0.3)
            w = bg_hills.get_width()
            start = -((camera_x // w) * w) - parallax
            for x in range(start, WIDTH + w, w):
                screen.blit(bg_hills, (x, HEIGHT - bg_hills.get_height() - 40))

        # khối tĩnh
        for b in world.blocks:
            draw_block(screen, b, camera_x)

        # platform
        for p in world.platforms:
            draw_platform(screen, p.rect, camera_x)

        # goal
        if world.goal:
            draw_goal(screen, world.goal, camera_x)

        # spikes
        for s in world.spikes:
            draw_spike_up(screen, s.rect, camera_x, active=s.is_active(now))

        # trigger debug
        if debug:
            for t in world.triggers:
                r = Rect(t.rect.x - camera_x, t.rect.y, t.rect.w, t.rect.h)
                pygame.draw.rect(screen, (180, 80, 200), r, 2)

        # player
        player.draw(screen, camera_x)

        # HUD
        hud = (
            "A/D hoặc ←/→: di chuyển   Space/Z/↑: nhảy   R: restart   F1: debug"
        )
        hud_surf = font.render(hud, True, WHITE)
        screen.blit(hud_surf, (16, 8))

        if state == STATE_DEAD:
            txt = big_font.render("BẠN ĐÃ CHẾT", True, RED)
            info = font.render(death_reason + "  (Nhấn R để chơi lại)", True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 160))
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 220))
        elif state == STATE_WON:
            txt = big_font.render("HOÀN THÀNH LEVEL!", True, GREEN)
            info = font.render("Nhấn R để chơi lại", True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 160))
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 220))

        pygame.display.flip()


if __name__ == "__main__":
    run()
