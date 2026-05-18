from __future__ import annotations
import pymysql
import os

import threading
from typing import Callable, Optional

import mysql.connector
from mysql.connector import Error as MySQLError

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

# ─────────────────────────────────────────────────────────────────────────────
# Konfigurasi koneksi  →  sesuaikan dengan environment kamu
# ─────────────────────────────────────────────────────────────────────────────
DB_CONFIG: dict = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "mager_db",
    "charset": "utf8mb4",
    "autocommit": True,
}
DB_PORTS = [3306, 3307]

TABLE_GAME = "games"


# ─────────────────────────────────────────────────────────────────────────────
# Helper: koneksi
# ─────────────────────────────────────────────────────────────────────────────
def get_connection():
    """Coba koneksi ke beberapa port MySQL menggunakan PyMySQL."""
    for port in DB_PORTS:
        try:
            conn = pymysql.connect(
                **DB_CONFIG,
                port=port
            )
            print(f"[DB GameDetail] Connected to MySQL port {port}")
            return conn
        except Exception as e: 
            print(f"[DB GameDetail] Failed port {port} -> {e}")

    raise Exception("Tidak bisa terhubung ke MySQL di port 3306 maupun 3307")


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

    rating = round(good / total * 100) if total > 0 else 0

    ACCENT_PALETTE = [
        "#3d85c8", "#c84b3d", "#3dc87a", "#c8b43d",
        "#8b3dc8", "#3dc8c8", "#c8783d",
    ]
    id_val = str(row.get("id_game") or "0")
    ac = ACCENT_PALETTE[abs(hash(id_val)) % len(ACCENT_PALETTE)]

    return {
        "id":             row.get("id_game"),
        "title":          row.get("nama_game", ""),
        "price":          float(row.get("harga_sekarang") or 0),
        "dev":            row.get("developer", ""),
        "pub":            row.get("publisher", ""),
        "rating":         rating,
        "img":            row.get("url_gambar", ""),
        "ac":             ac,
        "release_date":   str(row.get("tanggal_rilis") or "-"),
        "description":    row.get("deskripsi", ""),
        "good_review":    good,
        "bad_review":     bad,
        "total_reviews":  total,
        "current_player": int(row.get("current_player") or 0),
        "peak_player":    int(row.get("peak_player")    or 0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fungsi sinkron
# ─────────────────────────────────────────────────────────────────────────────
def fetch_game_by_id(game_id: int) -> Optional[dict]:
    """Ambil satu game dari DB berdasarkan id_game."""
    sql = "SELECT * FROM game WHERE id_game = %s LIMIT 1"
    try:
        conn = get_connection()
        # dictionary=True agar row bisa diakses dengan nama kolom
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql, (game_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return _row_to_game(row) if row else None
    except MySQLError as exc:
        print(f"[profileGame_logic] DB error: {exc}")
        return None


def fetch_price_history(game_id: int) -> list[dict]:
    sql = """
        SELECT tanggal, harga_reguler, harga_diskon
        FROM history_price
        WHERE id_game = %s
        ORDER BY tanggal ASC
    """
    try:
        conn = get_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql, (game_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "date":     str(r["tanggal"])[:10],   # ambil YYYY-MM-DD saja
                "price":    float(r["harga_diskon"] or r["harga_reguler"] or 0),
                "regular":  float(r["harga_reguler"] or 0),
                "discount": float(r["harga_diskon"]  or 0),
            }
            for r in rows
        ]
    except MySQLError as e:
        print(f"[profileGame_logic] Price history error: {e}")
        return []


def fetch_genres(game_id: int) -> list[str]:
    """Ambil semua genre untuk sebuah game dari tabel detail_genre JOIN genre."""
    sql = """
        SELECT g.nama_genre
        FROM detail_genre dg
        JOIN genre g ON dg.id_genre = g.id_genre
        WHERE dg.id_game = %s
        ORDER BY g.nama_genre ASC
    """
    try:
        conn = get_connection()
        cur = conn.cursor()          # tuple cursor sudah cukup, cuma satu kolom
        cur.execute(sql, (game_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0] for r in rows]
    except MySQLError as exc:
        print(f"[profileGame_logic] Genre error: {exc}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Worker sinyal
# ─────────────────────────────────────────────────────────────────────────────
class _GameDetailSignals(QObject):
    """Sinyal yang dikirim dari thread pool ke main thread."""
    game_ready    = pyqtSignal(object)   # dict | None
    history_ready = pyqtSignal(list)     # list[dict]
    genre_ready   = pyqtSignal(list)     # list[str]  ← TAMBAH
    error         = pyqtSignal(str)


class _FetchGameWorker(QRunnable):
    """Runnable: fetch game + price history + genre di thread terpisah."""

    def __init__(self, game_id: int, signals: _GameDetailSignals):
        super().__init__()
        self.game_id = game_id
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        # 1. Data utama game
        game = fetch_game_by_id(self.game_id)
        if game is None:
            self.signals.error.emit(f"Game id={self.game_id} tidak ditemukan.")
            self.signals.game_ready.emit(None)
            return
        self.signals.game_ready.emit(game)

        # 2. Riwayat harga
        history = fetch_price_history(self.game_id)
        self.signals.history_ready.emit(history)

        # 3. Genre
        genres = fetch_genres(self.game_id)
        self.signals.genre_ready.emit(genres)


# ─────────────────────────────────────────────────────────────────────────────
# GameDetailLoader
# ─────────────────────────────────────────────────────────────────────────────
class GameDetailLoader(QObject):
    game_ready    = pyqtSignal(object)   # dict | None
    history_ready = pyqtSignal(list)     # list[dict]
    genre_ready   = pyqtSignal(list)     # list[str]
    error         = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _GameDetailSignals()

        # Forward sinyal internal → sinyal publik
        self._signals.game_ready.connect(self.game_ready)
        self._signals.history_ready.connect(self.history_ready)
        self._signals.genre_ready.connect(self.genre_ready)
        self._signals.error.connect(self.error)

    def load(self, game_id: int):
        """Mulai fetch async. Hasilnya dikirim lewat sinyal."""
        # Menggunakan self.worker agar tidak dihapus otomatis oleh Garbage Collector Python
        self.worker = _FetchGameWorker(game_id, self._signals)
        QThreadPool.globalInstance().start(self.worker)
# ─────────────────────────────────────────────────────────────────────────────
# ImageFetcher
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
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.signals.done.emit(resp.read())
        except Exception as e:
            print(f"[DEBUG] Fetch error: {e}")
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
# Helpers format
# ─────────────────────────────────────────────────────────────────────────────
def fmt_price(price: float) -> str:
    if price == 0:
        return "Gratis"
    return "Rp {:,.0f}".format(price).replace(",", ".")


def fmt_number(n: int) -> str:
    return "{:,}".format(n).replace(",", ".")


def rating_label(rating: int) -> str:
    if rating >= 90:
        return "Excellent"
    if rating >= 70:
        return "Good"
    if rating >= 50:
        return "Mixed"
    return "Negative"