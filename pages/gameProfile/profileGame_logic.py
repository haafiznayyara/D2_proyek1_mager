"""
profileGame_logic.py  –  MAGER
Mengambil data detail game dari MySQL berdasarkan id_game,
lalu memetakannya ke dict yang siap dikonsumsi GameDetailWindow.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

import mysql.connector
from mysql.connector import Error as MySQLError

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

# ─────────────────────────────────────────────────────────────────────────────
# Konfigurasi koneksi  →  sesuaikan dengan environment kamu
# ─────────────────────────────────────────────────────────────────────────────
DB_CONFIG: dict = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",          # ← ganti
    "database": "mager_db",  # ← ganti
    "charset":  "utf8mb4",
    "autocommit": True,
}

# Nama tabel games di database
TABLE_GAMES = "games"


# ─────────────────────────────────────────────────────────────────────────────
# Helper: koneksi
# ─────────────────────────────────────────────────────────────────────────────
def _get_connection():
    """Buka koneksi baru ke MySQL. Lempar MySQLError jika gagal."""
    return mysql.connector.connect(**DB_CONFIG)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: mapping row DB → dict UI
# ─────────────────────────────────────────────────────────────────────────────
def _row_to_game(row: dict) -> dict:
    """
    Mapping kolom MySQL → dict yang dipakai GameDetailWindow & GameCard.

    Kolom DB  : id_game, nama_game, genre, harga_sekarang, developer,
                publisher, current_player, peak_player,
                good_review, bad_review, url_gambar,
                tanggal_rilis, deskripsi
    """
    good  = int(row.get("good_review") or 0)
    bad   = int(row.get("bad_review")  or 0)
    total = good + bad

    # Rating 0-100 dihitung dari rasio good review
    rating = round(good / total * 100) if total > 0 else 0

    # Warna aksen placeholder  (cycling dari palette kecil)
    ACCENT_PALETTE = [
        "#3d85c8", "#c84b3d", "#3dc87a", "#c8b43d",
        "#8b3dc8", "#3dc8c8", "#c8783d",
    ]
    ac = ACCENT_PALETTE[int(row.get("id_game") or 0) % len(ACCENT_PALETTE)]

    return {
        # ── field wajib (dipakai dashboard_ui & profileGame_ui) ──
        "id":             row.get("id_game"),
        "title":          row.get("nama_game", ""),
        "genre":          row.get("genre", ""),
        "price":          float(row.get("harga_sekarang") or 0),
        "dev":            row.get("developer", ""),
        "pub":            row.get("publisher", ""),
        "rating":         rating,
        "img":            row.get("url_gambar", ""),
        "ac":             ac,

        # ── field tambahan (hanya profileGame_ui) ──
        "release_date":   str(row.get("tanggal_rilis") or "-"),
        "description":    row.get("deskripsi", ""),
        "good_review":    good,
        "bad_review":     bad,
        "total_reviews":  total,
        "current_player": int(row.get("current_player") or 0),
        "peak_player":    int(row.get("peak_player")    or 0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fungsi sinkron  (bisa dipanggil langsung jika mau)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_game_by_id(game_id: int) -> Optional[dict]:
    """
    Ambil satu game dari DB berdasarkan id_game.
    Return dict game, atau None jika tidak ditemukan / error.
    """
    sql = f"SELECT * FROM `{TABLE_GAMES}` WHERE id_game = %s LIMIT 1"
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute(sql, (game_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return _row_to_game(row) if row else None
    except MySQLError as exc:
        print(f"[profileGame_logic] DB error: {exc}")
        return None


def fetch_price_history(game_id: int) -> list[dict]:
    """
    Ambil riwayat harga dari tabel price_history (jika ada).
    Kembalikan list dict {'date': str, 'price': float} terurut ascending.
    Jika tabel tidak ada, kembalikan list kosong.
    """
    sql = """
        SELECT tanggal, harga
        FROM price_history
        WHERE id_game = %s
        ORDER BY tanggal ASC
    """
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute(sql, (game_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"date": str(r["tanggal"]), "price": float(r["harga"])} for r in rows]
    except MySQLError:
        # Tabel mungkin belum ada — kembalikan list kosong (UI pakai data dummy)
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Worker sinyal  (untuk async Qt)
# ─────────────────────────────────────────────────────────────────────────────
class _GameDetailSignals(QObject):
    """Sinyal yang dikirim dari thread pool ke main thread."""
    game_ready    = pyqtSignal(object)   # dict | None
    history_ready = pyqtSignal(list)     # list[dict]
    error         = pyqtSignal(str)


class _FetchGameWorker(QRunnable):
    """Runnable: fetch game + price history di thread terpisah."""

    def __init__(self, game_id: int, signals: _GameDetailSignals):
        super().__init__()
        self.game_id = game_id
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        game = fetch_game_by_id(self.game_id)
        if game is None:
            self.signals.error.emit(f"Game id={self.game_id} tidak ditemukan.")
            self.signals.game_ready.emit(None)
            return

        self.signals.game_ready.emit(game)

        history = fetch_price_history(self.game_id)
        self.signals.history_ready.emit(history)


# ─────────────────────────────────────────────────────────────────────────────
# GameDetailLoader  –  kelas utama yang dipakai Router / profileGame_ui
# ─────────────────────────────────────────────────────────────────────────────
class GameDetailLoader(QObject):
    """
    Cara pakai dari Router / ProfileGameWindow:

        loader = GameDetailLoader()
        loader.game_ready.connect(detail_window.load_game)
        loader.history_ready.connect(detail_window.load_price_history)
        loader.error.connect(lambda msg: print("Error:", msg))
        loader.load(game_id)

    Semua callback dipanggil di main thread (aman untuk update UI).
    """

    game_ready    = pyqtSignal(object)   # dict | None
    history_ready = pyqtSignal(list)     # list[dict]
    error         = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _GameDetailSignals()

        # Forward sinyal internal → sinyal publik
        self._signals.game_ready.connect(self.game_ready)
        self._signals.history_ready.connect(self.history_ready)
        self._signals.error.connect(self.error)

    def load(self, game_id: int):
        """Mulai fetch async. Hasilnya dikirim lewat sinyal game_ready."""
        worker = _FetchGameWorker(game_id, self._signals)
        QThreadPool.globalInstance().start(worker)


# ─────────────────────────────────────────────────────────────────────────────
# ImageFetcher  –  sama persis seperti di dashboard_logic
# (disertakan di sini agar profileGame_ui tidak perlu import dashboard_logic)
# ─────────────────────────────────────────────────────────────────────────────
class _ImageSignals(QObject):
    done = pyqtSignal(bytes)


class _ImageRunnable(QRunnable):
    def __init__(self, url: str, signals: _ImageSignals):
        super().__init__()
        self.url     = url
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
      try:
          import urllib.request
          req = urllib.request.Request(
              self.url,
              headers={"User-Agent": "Mozilla/5.0"}  # ← tambah ini
          )
          with urllib.request.urlopen(req, timeout=10) as resp:
              self.signals.done.emit(resp.read())
      except Exception as e:
          print(f"[DEBUG] Fetch error: {e}")  # ← agar error terlihat
          self.signals.done.emit(b"")


class ImageFetcher(QObject):
    done = pyqtSignal(bytes)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url      = url
        self._signals = _ImageSignals()
        self._signals.done.connect(self.done)

    def fetch_async(self):
        worker = _ImageRunnable(self.url, self._signals)
        QThreadPool.globalInstance().start(worker)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers format  (dipakai profileGame_ui agar tidak import dashboard_logic)
# ─────────────────────────────────────────────────────────────────────────────
def fmt_price(price: float) -> str:
    if price == 0:
        return "Gratis"
    return "Rp {:,.0f}".format(price).replace(",", ".")


def fmt_number(n: int) -> str:
    """Contoh: 1051810 → '1.051.810'"""
    return "{:,}".format(n).replace(",", ".")


def rating_label(rating: int) -> str:
    if rating >= 90:
        return "Excellent"
    if rating >= 70:
        return "Good"
    if rating >= 50:
        return "Mixed"
    return "Negative"