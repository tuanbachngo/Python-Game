"""Game package."""
__version__ = "0.1.0"

# Re-export tiện dùng
from .core import constants, GameSettings, levels
from .ui import HUD, MenuManager
from .world import Block, MovingPlatform, Spike , HiddenSpike, Checkpoint, World
from .entities import Player
