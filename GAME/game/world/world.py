import pygame
from .tiles import Block, MovingPlatform, Spike, HiddenSpike, Checkpoint, FakeCheckpoint, DelayCheckpoint, LevelGate # Level 1
from .tiles import Tide, Water, BubbleManager, Wall, Connected_Block, Half_Block, Stone, SimpleMovingWall, Moving_wall, spawn_arrow_traps, ScreenShake # Level 2
from .tiles import Switch, BubbleSpout
from ..entities.player import Player
TILE = 48 
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
        self.tides = []           # + (sóng)
        self.water = []           # ~ (nước)
        self.switches = []
        self.bubble_spouts = []   # R 
        self.is_full_underwater = (level_id ==4)
        self.walls = []           # W (tường rắn)
        self.c_block = []         # O (connected block)
        self.h_block = []         # B (half block)
        self.stones = []          # S (đá lăn)
        self.shake = ScreenShake()
        self.fragments = []       # mảnh vỡ tường, nếu Stone tạo ra
        self.moving_walls = []    # M (nếu dùng cho moving_wall)
        self.simple_walls = []    # N (tường trượt đơn giản)
        self.arrows = []          # bẫy mũi tên
        self.bubble_manager = None  # quản lý bóng nước
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
                    self.checkpoints.append(Checkpoint(x, y,world_ref=self))
                elif ch == 'F':
                    self.checkpoints.append(FakeCheckpoint(x, y,world_ref=self))
                elif ch == 'D':
                    self.checkpoints.append(DelayCheckpoint(x, y,world_ref=self))
                elif ch == 'E':
                    self.checkpoints.append(LevelGate(x, y))
                elif ch == 'M':
                    self.blocks.append(MovingPlatform(x,y,dx=2,dy=0,move_range=150))
                elif ch == 'L':
                    self.blocks.append(MovingPlatform(x,y,dx=-2,dy=0,move_range=150))
                elif ch == 'H':
                    self.spikes.append(HiddenSpike(x, y, delay = 15000))
                elif ch == 'G':
                    self.spikes.append(HiddenSpike(x, y, delay = 16000))

                elif ch == '+':      # sóng
                    self.tides.append(Tide(x, y))
                elif ch == '~':      # nước
                    self.water.append(Water(x, y))
                elif ch == 'Q':      # switch
                    self.switches.append(Switch(x, y))
                elif ch == 'R':      # bubble
                    self.bubble_spouts.append(BubbleSpout(x, y))
                elif ch == 'W':      # tường rắn
                    self.walls.append(Wall(x, y))
                elif ch == 'O':      # connected block
                    self.c_block.append(Connected_Block(x, y))
                elif ch == 'B':      # half block
                    self.h_block.append(Half_Block(x, y))
                elif ch == 'S':      # đá lăn
                    stone = Stone(x, y)
                    stone.trigger1_x = 90
                    stone.trigger2_x = 700
                    stone.trigger3_x = 300
                    self.stones.append(stone)
                elif ch == 'N':      
                    self.simple_walls.append(SimpleMovingWall(x, y))
                elif ch == 'X':
                    self.moving_walls.append(Moving_wall(x, y))
                elif ch == 'b' and not bubble_spawn_found:
                    self.bubble_manager = BubbleManager(
                        spawn_interval_ms=2800,
                        spawn_x=x,
                        spawn_y=y
                    )
                    bubble_spawn_found = True
                elif ch == 'A':  # vùng nước cho trap mũi tên
                    self.water.append(Water(x, y))    

        if self.bubble_manager is None:
            # không spawn bóng nhưng vẫn có manager để không bị None
            self.bubble_manager = BubbleManager(spawn_interval_ms=1000000)
                    
        self.player = Player(*self.player_start, initial_health=player_health)

        if self.is_full_underwater:
            self.player.full_under_world = True
            self.player.idle_underwater = True
            self.player.swim_leave_time = None

    def solids(self):
        return self.blocks + self.walls + self.c_block + self.h_block + self.fragments

    def update(self, dt):
        for b in self.blocks:
            if isinstance(b, MovingPlatform):
                    b.update()

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
        # self.player.in_water = False 

        if self.is_full_underwater:
            # Room cuối: luôn là nước
            self.player.idle_underwater = True
            self.player.swim_leave_time = None
        else:
            # Room bình thường: Water block mới cập nhật idle underwater
            for wa in self.water:
                wa.update(self.player)
                
        for arr in self.arrows:
            arr.update(self.player, self.solids())

        # Switch: kiểm tra va chạm & bật gravity_effect_active
        for sw in self.switches:
            sw.update(self.player, self)

        # BubbleSpout: animation + đẩy player
        for spout in self.bubble_spouts:
            spout.update()
            spout.check_collision_and_knockback(self.player)

        self.bubble_manager.update(player = self.player)
        # update screen shake WITH dt (ms)
        self.shake.update(dt)

    def draw_background(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0,0))

    def draw(self, surface):

        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))

        ox, oy = self.shake.get_offset()
        for w in self.walls:
            w.draw(surface)
        for sp in self.spikes:
            sp.draw(surface)
        for st in self.stones:
            st.draw(surface, ox, oy)
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
        for sw in self.switches:
            sw.draw(surface, ox, oy)
        for spout in self.bubble_spouts:
            spout.draw(surface, ox, oy)
                
        self.bubble_manager.draw(surface, ox, oy)
        self.player.draw(surface, ox, oy)