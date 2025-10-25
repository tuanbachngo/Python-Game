import sys, math, pygame, os
from pygame import Rect

ASSETS = {}

def load_image(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    return img

def try_load(path, scale=None):
    return load_image(path, scale) if os.path.exists(path) else None

def load_sheet_horz(path, frame_w=None, frame_h=None, scale=None):
    """Cắt spritesheet ghép NGANG thành list frame.
    Mặc định mỗi frame là hình vuông có cạnh = chiều cao ảnh."""
    surf = try_load(path)
    if not surf:
        return []
    w, h = surf.get_width(), surf.get_height()
    if frame_h is None:
        frame_h = h
    if frame_w is None:
        frame_w = frame_h  # frame vuông
    frames = []
    x = 0
    while x + frame_w <= w:
        frame = surf.subsurface((x, 0, frame_w, frame_h)).copy()
        if scale:
            frame = pygame.transform.smoothscale(frame, scale)
        frames.append(frame)
        x += frame_w
    return frames

def load_assets():
    base = os.path.join(os.path.dirname(__file__), "assets")
    a = {}
    # Tiles
    a["tile_block"]    = try_load(os.path.join(base, "tiles", "block.png"), (TILE, TILE))
    a["tile_platform"] = try_load(os.path.join(base, "tiles", "platform.png"), (TILE, TILE))
    a["tile_spike_up"] = try_load(os.path.join(base, "tiles", "spike_up.png"), (TILE, TILE)) \
                         or try_load(os.path.join(base, "tiles", "spike.png"), (TILE, TILE))  # fallback
    # Props
    a["goal"] = try_load(os.path.join(base, "props", "door.png"), (TILE, TILE))
    # Background
    a["bg_sky"]   = try_load(os.path.join(base, "bg", "bg_sky.png"), (WIDTH, HEIGHT))
    a["bg_hills"] = try_load(os.path.join(base, "bg", "bg_hills.png"))  # parallax, không scale

    # Player (ưu tiên spritesheet; nếu thiếu thì fallback về file lẻ)
    a["player_idle"] = load_sheet_horz(os.path.join(base, "player", "idle_sheet.png"), 48, 48, None) \
        or [p for p in [try_load(os.path.join(base, "player", "idle_0.png"))] if p]
    a["player_run"]  = load_sheet_horz(os.path.join(base, "player", "run_sheet.png"), 48, 48, None) \
        or [img for i in range(4) if (img := try_load(os.path.join(base, "player", f"run_{i}.png")))]
    a["player_jump"] = load_sheet_horz(os.path.join(base, "player", "jump_sheet.png"), 48, 48, None) \
        or [img for i in range(2) if (img := try_load(os.path.join(base, "player", f"jump_{i}.png")))]
    a["player_dead"] = load_sheet_horz(os.path.join(base, "player", "dead_sheet.png"), 48, 48, None) \
        or [img for i in range(7) if (img := try_load(os.path.join(base, "player", f"dead_{i}.png")))]

    # FX sheets (tùy chọn, nếu không có sẽ bỏ qua)
    a["fx_jump"] = load_sheet_horz(os.path.join(base, "extras", "jumping-effect-sheet.png"), 32, 32, None)
    a["fx_fly"]  = load_sheet_horz(os.path.join(base, "extras", "running-effect-sheet.png"), 32, 32, None)
    a["fx_die"]  = load_sheet_horz(os.path.join(base, "extras", "dying-effect-sheet.png"),   32, 32, None)

    # Fallback: nếu thiếu platform.png thì dùng luôn block.png để đỡ vỡ hình
    if not a.get("tile_platform") and a.get("tile_block"):
        a["tile_platform"] = a["tile_block"]
    return a

# ------------------------------
# CÀI ĐẶT CƠ BẢN
# ------------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48
# ------------------------------
# Vật lý đơn giản
GRAVITY = 0.32
#Gia tốc rơi. Mỗi frame, vận tốc dọc tăng thêm 0.6 px/frame (hướng xuống).
#Tăng số này → rơi nhanh, nhảy “nặng”.
#Giảm → rơi chậm, cảm giác “floaty”.
MAX_FALL = 14
#Giới hạn vận tốc rơi tối đa (terminal velocity).
#Giúp tránh tăng tốc vô hạn khi rơi xa; ổn định va chạm.
#Quá thấp → rơi lơ lửng; quá cao → dễ “đâm xuyên” nếu code va chạm không tách trục kỹ.
PLAYER_SPEED = 4.2
JUMP_VEL = -13
#Vận tốc nhảy ban đầu (âm = hướng lên). Ở 60 FPS → -12×60 = -720 px/s.
#|giá trị| lớn hơn → nhảy vút cao hơn; nhỏ hơn → nhảy thấp.
COYOTE_MS = 110  # nhảy "cứu cánh" sau khi rời đất ~0.12s
#“Coyote time”: khoảng thời gian sau khi rời đất vẫn cho phép nhảy.
#120 ms ≈ 7 frames ở 60 FPS (120/1000×60 ≈ 7.2).
#Tăng chút giúp điều khiển “bám tay”; quá nhiều thì cảm giác gian lận.
# ------------------------------
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
# Thêm: 'M' = moving platform ngang (qua lại 144px, 2 px/frame)
LEVEL_MAP = [
    "########################",  # 24 cột => 24 * 48 = 1152px (có cuộn màn hình)
    "#.......................",
    "#......................",
    "#.......................",
    "#..P..............T.....",
    "#..................T....",
    "#..............F....G...",
    "#.......................",
    "#.......................",
    "###############^^^^^^^^^#",
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

def draw(self, screen, scroll_x):
    now = pygame.time.get_ticks()
    if not self.alive:
        frames = ASSETS["player_dead"]
        idx = min(self.current_frame, max(0, len(frames)-1))
        img = frames[idx] if frames else None
    elif not self.on_ground:
        frames = ASSETS["player_jump"]
        img = frames[(now // 100) % len(frames)] if frames else None
    elif self.is_running:
        frames = ASSETS["player_run"]
        img = frames[(now // 90) % len(frames)] if frames else None
    else:
        frames = ASSETS["player_idle"]
        img = frames[(now // 120) % len(frames)] if frames else None

    if img is None:
        return  # thiếu asset thì thôi

    if self.direction == -1:
        img = pygame.transform.flip(img, True, False)

    screen.blit(img, (self.rect.x - scroll_x - 8, self.rect.y - 6))
# ------------------------------
# THỰC THỂ TRÒ CHƠI
# ------------------------------


# Bind free function to Player class for method-style call
# Player.draw = draw  # (disabled, we call draw(player, ...) instead)
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
        self.direction = 1
        self.is_running = False
        self.alive = True

    def handle_input(self, keys):
        ax = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += 1
        self.vel_x = ax * PLAYER_SPEED
        self.is_running = (ax != 0)
        if ax != 0:
            self.direction = 1 if ax > 0 else -1

    def try_jump(self, jump_down, now_ms):
        jumped = False
        if jump_down and not self._jump_was_down:
            if self.on_ground or self.coyote_ms > 0:
                self.vel_y = JUMP_VEL
                self.on_ground = False
                self.coyote_ms = 0
                jumped = True
        self._jump_was_down = jump_down
        return jumped

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
class Animation:
    def __init__(self, frames, frame_ms=70, loop=False):
        self.frames = frames or []
        self.frame_ms = frame_ms
        self.loop = loop
        self.start_ms = pygame.time.get_ticks()
        self.alive = True

    def current(self, now):
        if not self.frames: self.alive = False; return None
        i = (now - self.start_ms) // self.frame_ms
        if self.loop:
            i = int(i % len(self.frames))
        else:
            if i >= len(self.frames):
                i = len(self.frames)-1
                self.alive = False
        return self.frames[int(i)]

class Fx:
    def __init__(self, x, y, frames, frame_ms=70, loop=False, vx=0, vy=0, anchor_bottom=True):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.anim = Animation(frames, frame_ms, loop)
        self.anchor_bottom = anchor_bottom

    def update(self, dt_ms):
        self.x += self.vx * (dt_ms / 16.666)
        self.y += self.vy * (dt_ms / 16.666)

    def alive(self, now):
        _ = self.anim.current(now)
        return self.anim.alive

    def draw(self, screen, cam_x, now):
        img = self.anim.current(now)
        if not img: return
        x = int(self.x - cam_x - img.get_width()//2)
        y = int(self.y - img.get_height()) if self.anchor_bottom else int(self.y - img.get_height()//2)
        screen.blit(img, (x, y))
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
        # khối + platform chưa rơi + moving
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
    fx_list: list[Fx] = []
    last_fly_emit = 0
    spawned_die_fx = False
    fx_list: list[Fx] = []
    last_fly_emit = 0
    spawned_die_fx = False

    state = STATE_PLAY
    death_reason = ""
    debug = False
    camera_x = 0

    def restart():
        nonlocal world, player, state, death_reason, camera_x, fx_list, last_fly_emit, spawned_die_fx
        world = World(LEVEL_MAP)
        player = Player(*world.player_start)
        state = STATE_PLAY
        death_reason = ""
        camera_x = 0
        fx_list.clear()
        last_fly_emit = 0
        spawned_die_fx = False
        player.alive = True

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
            did_jump = player.try_jump(jump_down, now)
            if did_jump and ASSETS.get('fx_jump'):
                fx_list.append(Fx(player.rect.centerx, player.rect.bottom, ASSETS['fx_jump'], frame_ms=60, loop=False, vy=0, anchor_bottom=True))
            player.apply_gravity()

            # platform arming (trước khi collide dọc xong ta sẽ set chính xác)
            for p in world.platforms:
                p.arm_if_player_on_top(player.rect, now)
                p.update(now)
            
            # flying effect: emit khi đang ở trên không và có vận tốc ngang
            if (not player.on_ground) and abs(player.vel_x) > 0.3 and ASSETS.get("fx_fly"):
                if now - last_fly_emit > 90:
                    spawn_x = player.rect.centerx - (12 if player.vel_x > 0 else -12)
                    fx_list.append(Fx(spawn_x, player.rect.bottom-4, ASSETS["fx_fly"], frame_ms=60, loop=False, vx=-player.vel_x*0.2))
                    last_fly_emit = now

# va chạm
            player.move_and_collide(world.solids())

# camera
            camera_x = max(0, min(player.rect.centerx - WIDTH // 2, world.level_px_w - WIDTH))

            # triggers
            for t in world.triggers:
                t.try_trigger(player.rect, now)

            # update FX
            for fx in list(fx_list):
                fx.update(dt_ms)
                if not fx.is_alive(now):
                    fx_list.remove(fx)

            # chết vì gai
            for sp in world.spikes:
                if sp.is_active(now) and player.rect.colliderect(sp.rect):
                    if not spawned_die_fx and ASSETS.get("fx_die"):
                        fx_list.append(Fx(player.rect.centerx, player.rect.bottom, ASSETS["fx_die"], frame_ms=60, loop=False, anchor_bottom=True))
                        spawned_die_fx = True
                    if not spawned_die_fx and ASSETS.get("fx_die"):
                        fx_list.append(Fx(player.rect.centerx, player.rect.bottom, ASSETS["fx_die"], frame_ms=60, loop=False, anchor_bottom=True))
                        spawned_die_fx = True
                    state = STATE_DEAD
                    death_reason = "Bạn dẫm vào gai!"
                    break

            # rơi khỏi map
            if player.rect.top > world.level_px_h + 200:
                if not spawned_die_fx and ASSETS.get("fx_die"):
                    fx_list.append(Fx(player.rect.centerx, player.rect.bottom, ASSETS["fx_die"], frame_ms=60, loop=False, anchor_bottom=True))
                    spawned_die_fx = True
                if not spawned_die_fx and ASSETS.get("fx_die"):
                    fx_list.append(Fx(player.rect.centerx, player.rect.bottom, ASSETS["fx_die"], frame_ms=60, loop=False, anchor_bottom=True))
                    spawned_die_fx = True
                state = STATE_DEAD
                player.alive = False
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
        draw(player, screen, camera_x)

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
