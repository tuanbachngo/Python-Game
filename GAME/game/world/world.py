import pygame
from .tiles import Block, MovingPlatform, Spike, HiddenSpike, Checkpoint
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