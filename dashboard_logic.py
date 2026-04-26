import threading
import urllib.request
from PyQt5.QtCore import pyqtSignal, QObject
from database.connection import connection_database

# ── Palette ───────────────────────────────────────────────────────────────
BG       = "#0d1117"
CARD     = "#161b22"
CARD_HOV = "#1c2330"
ACCENT   = "#00e676"
ACCENT2  = "#00bcd4"
TEXT1    = "#e6edf3"
TEXT2    = "#8b949e"
TEXT3    = "#58a6ff"
BORDER   = "#21262d"
TAG_BG   = "#21262d"

COLS       = 5
GAP        = 12
INFO_H     = 170
COVER_RATIO = 7 / 15

CATEGORIES = [
    "Semua", "Action", "Action RPG", "RPG", "Simulation",
    "Platformer", "Roguelite", "Open World", "Survival Horror",
]


def get_games_from_db():
    try:
        conn = connection_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game")
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        games = []
        for row in results:
            # Hitung rating 0-100 dari rasio good/bad review
            good  = int(row.get("good_review") or 0)
            bad   = int(row.get("bad_review")  or 0)
            total = good + bad
            rating = round(good / total * 100) if total > 0 else 0

            games.append({
                "id":             row.get("id_game"),        # ← tambah id
                "title":          row.get("nama_game"),
                "genre":          row.get("genre"),
                "dev":            row.get("developer"),
                "pub":            row.get("publisher"),
                "price":          row.get("harga_sekarang") or 0,
                "rating":         rating,                    # ← fix rating
                "img":            row.get("url_gambar") or "",
                "ac":             "#00e676",
                # ── field untuk detail page ──
                "release_date":   str(row.get("tanggal_rilis") or "-"),
                "description":    row.get("deskripsi") or "",
                "good_review":    good,
                "bad_review":     bad,
                "total_reviews":  total,
                "current_player": int(row.get("current_player") or 0),
                "peak_player":    int(row.get("peak_player")    or 0),
            })
        return games

    except Exception as e:
        print("ERROR DB:", e)
        return []


def fmt_price(p):
    if p == 0:
        return "Gratis"
    return "Rp " + f"{p:,}".replace(",", ".")


def rating_color(r):
    if r >= 90:
        return "#22c55e"
    if r >= 75:
        return "#f59e0b"
    return "#ef4444"


def filter_games(all_games, cat, query=""):
    query = query.lower().strip()
    filtered = []
    for g in all_games:
        if cat != "Semua" and g["genre"] != cat:
            continue
        if query and query not in g["title"].lower() and query not in g["dev"].lower():
            continue
        filtered.append(g)
    return filtered


class ImageFetcher(QObject):
    """Download gambar dari URL di thread terpisah, emit signal saat selesai."""
    done = pyqtSignal(bytes)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def fetch(self):
        try:
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            self.done.emit(data)
        except Exception:
            self.done.emit(b"")

    def fetch_async(self):
        t = threading.Thread(target=self.fetch, daemon=True)
        t.start()