from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "pygame_assets"

def asset(name: str) -> str:
    return str(ASSETS_DIR / name)

