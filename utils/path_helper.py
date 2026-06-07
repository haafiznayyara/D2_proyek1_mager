import sys
import os

def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        # Pakai _MEIPASS — folder temp tempat PyInstaller ekstrak semua file
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR   = get_base_dir()
POSTER_DIR = os.path.join(BASE_DIR, "assets", "posters")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")