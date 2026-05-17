import threading
import urllib.request
from PyQt5.QtCore import pyqtSignal, QObject
from difflib import SequenceMatcher
from database.connection import connection_database

# ── Palette ───────────────────────────────────────────────────────────────
BG       = "#0A1123"
CARD     = "#1A2332"
CARD_HOV = "#1A2332"
ACCENT   = "#4ADE80"
ACCENT2  = "#4ADE80"
TEXT1    = "#FFFFFF"
TEXT2    = "#8B96A5"
BORDER   = "#2A3647"
TAG_BG   = "#2A3647"

COLS       = 5
GAP        = 12
INFO_H     = 183
COVER_RATIO = 0.58

def get_categories_from_db() -> list:
    try:
        conn = connection_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.nama_genre, COUNT(dg.id_game) as jumlah
            FROM genre g
            LEFT JOIN detail_genre dg ON g.id_genre = dg.id_genre
            GROUP BY g.id_genre, g.nama_genre
            ORDER BY jumlah DESC, g.nama_genre
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        genres = [row.get("nama_genre") for row in rows if row.get("nama_genre")]
        return ["Semua"] + genres
    except Exception as e:
        print("ERROR DB (categories):", e)
        return ["Semua"]


# def get_games_from_db():
#     try:
#         conn = connection_database()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM game")
#         results = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         games = []
#         for row in results:
#             # Hitung rating 0-100 dari rasio good/bad review
#             good  = int(row.get("good_review") or 0)
#             bad   = int(row.get("bad_review")  or 0)
#             total = good + bad
#             rating = round(good / total * 100) if total > 0 else 0

#             games.append({
#                 "id":             row.get("id_game"),        # ← tambah id
#                 "title":          row.get("nama_game"),
#                 "genre":          row.get("genre"),
#                 "dev":            row.get("developer"),
#                 "pub":            row.get("publisher"),
#                 "price":          row.get("harga_sekarang") or 0,
#                 "rating":         rating,                    # ← fix rating
#                 "img":            row.get("url_gambar") or None,
#                 "ac":             "#00e676",
#                 # ── field untuk detail page ──
#                 "release_date":   str(row.get("tanggal_rilis") or "-"),
#                 "description":    row.get("deskripsi") or "",
#                 "good_review":    good,
#                 "bad_review":     bad,
#                 "total_reviews":  total,
#                 "current_player": int(row.get("current_player") or 0),
#                 "peak_player":    int(row.get("peak_player")    or 0),
#             })
#         return games

#     except Exception as e:
#         print("ERROR DB:", e)
#         return []

def get_games_from_db():
    try:
        conn = connection_database()
        cursor = conn.cursor()

        # Ambil semua game
        cursor.execute("SELECT * FROM game")
        games_raw = cursor.fetchall()

        # Ambil semua detail_genre sekaligus (1 query, lebih efisien)
        cursor.execute("""
            SELECT dg.id_game, g.nama_genre
            FROM detail_genre dg
            JOIN genre g ON dg.id_genre = g.id_genre
        """)
        genre_rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Kelompokkan genre per id_game → { id_game: ["Action", "RPG", ...] }
        genre_map = {}
        for row in genre_rows:
            id_game    = row.get("id_game")
            nama_genre = row.get("nama_genre") or ""
            if id_game not in genre_map:
                genre_map[id_game] = []
            if nama_genre:
                genre_map[id_game].append(nama_genre)

        games = []
        for row in games_raw:
            good  = int(row.get("good_review") or 0)
            bad   = int(row.get("bad_review")  or 0)
            total = good + bad
            rating = round(good / total * 100) if total > 0 else 0

            id_game = row.get("id_game")
            genres  = genre_map.get(id_game, [])

            games.append({
                "id":             id_game,
                "title":          row.get("nama_game"),
                "genre":          genres[0] if genres else "",   # genre utama (untuk filter)
                "genres":         genres,                         # semua genre (untuk tag pills)
                "tags":           genres,                         # alias untuk popular_card
                "dev":            row.get("developer"),
                "pub":            row.get("publisher"),
                "price":          row.get("harga_sekarang") or 0,
                "rating":         rating,
                "img":            row.get("url_gambar") or None,
                "ac":             "#00e676",
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

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def filter_games(all_games, cat, query=""):
    query = query.lower().strip()
    keywords = query.split()

    filtered = []

    for g in all_games:
        if cat != "Semua" and cat not in g.get("genres", []):
            continue

        if not query:
            filtered.append(g)
            continue

        title = (g.get("title") or "").lower()
        dev = (g.get("dev") or "").lower()
        pub = (g.get("pub") or "").lower()
        genres = " ".join(g.get("genres", [])).lower()

        searchable_text = f"{title} {dev} {pub} {genres}"
        searchable_words = searchable_text.split()

        exact_match = all(
            keyword in searchable_text
            for keyword in keywords
        )

        fuzzy_match = all(
            any(
                keyword in word or similarity(keyword, word) >= 0.72
                for word in searchable_words
            )
            for keyword in keywords
        )

        if exact_match or fuzzy_match:
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