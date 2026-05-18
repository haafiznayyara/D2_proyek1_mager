from __future__ import annotations
import pymysql
import os

from typing import Optional

import pymysql
import pymysql.cursors

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from database.connection import connection_database

# Nama tabel — samakan dengan dashboard
TABLE_GAMES = "game"


# ─────────────────────────────────────────────────────────────────────────────
# Helper koneksi
# ─────────────────────────────────────────────────────────────────────────────
def _conn_read():
    """Koneksi read — pakai helper bersama (DictCursor, autocommit=True)."""
    return connection_database()


def _conn_write():
    """
    Koneksi write — autocommit=False agar bisa commit/rollback manual.
    Tetap pakai DictCursor supaya row.get() bekerja di semua query.
    """
    ports = [3306, 3307]
    for port in ports:
        try:
            conn = pymysql.connect(
                host="localhost",
                port=port,
                user="root",
                password="",
                database="mager_db",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
            print(f"[write_conn] Connected port {port}")
            return conn
        except pymysql.MySQLError:
            print(f"[write_conn] Failed port {port}")
    raise pymysql.MySQLError(
        "Tidak bisa terhubung ke MySQL di port 3306 maupun 3307"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper: mapping row DB → dict UI
# ─────────────────────────────────────────────────────────────────────────────
def _row_to_game(row: dict) -> dict:
    good  = int(row.get("good_review") or 0)
    bad   = int(row.get("bad_review")  or 0)
    total = good + bad
    rating = round(good / total * 100) if total > 0 else 0

    ACCENT_PALETTE = [
        "#3d85c8", "#c84b3d", "#3dc87a", "#c8b43d",
        "#8b3dc8", "#3dc8c8", "#c8783d",
    ]
    # Pakai hash() supaya aman untuk UUID string maupun int
    ac = ACCENT_PALETTE[abs(hash(str(row.get("id_game") or ""))) % len(ACCENT_PALETTE)]

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
# Fungsi sinkron — dipanggil dari thread pool, BUKAN main thread
# ─────────────────────────────────────────────────────────────────────────────
def fetch_game_by_id(game_id) -> Optional[dict]:
    sql = f"SELECT * FROM `{TABLE_GAMES}` WHERE id_game = %s LIMIT 1"
    try:
        conn = _conn_read()
        with conn.cursor() as cur:
            cur.execute(sql, (game_id,))
            row = cur.fetchone()
        conn.close()
        return _row_to_game(row) if row else None
    except Exception as exc:
        print(f"[fetch_game_by_id] Error: {exc}")
        return None


def fetch_price_history(game_id) -> list[dict]:
    sql = """
        SELECT tanggal, harga_reguler, harga_diskon
        FROM history_price
        WHERE id_game = %s
        ORDER BY tanggal ASC
    """
    try:
        conn = _conn_read()
        with conn.cursor() as cur:
            cur.execute(sql, (game_id,))
            rows = cur.fetchall()
        conn.close()
        return [
            {
                "date":     str(r["tanggal"])[:10],
                "price":    float(r["harga_diskon"] or r["harga_reguler"] or 0),
                "regular":  float(r["harga_reguler"] or 0),
                "discount": float(r["harga_diskon"]  or 0),
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[fetch_price_history] Error: {e}")
        return []


def fetch_genres(game_id) -> list[str]:
    sql = """
        SELECT g.nama_genre
        FROM detail_genre dg
        JOIN genre g ON dg.id_genre = g.id_genre
        WHERE dg.id_game = %s
        ORDER BY g.nama_genre ASC
    """
    try:
        conn = _conn_read()
        with conn.cursor() as cur:
            cur.execute(sql, (game_id,))
            rows = cur.fetchall()
        conn.close()
        return [r["nama_genre"] for r in rows if r.get("nama_genre")]
    except Exception as exc:
        print(f"[fetch_genres] Error: {exc}")
        return []


def fetch_reviews(game_id) -> list[dict]:
    """Ambil semua review, JOIN users untuk username."""
    sql = """
        SELECT
            r.id_review,
            u.username,
            r.review_gameplay,
            r.review_cerita,
            r.review_grafik
        FROM review r
        JOIN users u ON r.id_user = u.id_user
        WHERE r.id_game = %s
        ORDER BY r.id_review DESC
    """
    try:
        conn = _conn_read()
        with conn.cursor() as cur:
            cur.execute(sql, (game_id,))
            rows = cur.fetchall()
        conn.close()
        print(f"[fetch_reviews] game_id={game_id}, dapat {len(rows)} baris")
        result = [
            {
                "id":       row["id_review"],
                "username": row.get("username") or "Anonim",
                "gameplay": row.get("review_gameplay") or "",
                "cerita":   row.get("review_cerita")   or "",
                "grafik":   row.get("review_grafik")   or "",
            }
            for row in rows
        ]
        return result
    except Exception as exc:
        print(f"[fetch_reviews] Error: {exc}")
        return []


def submit_review(game_id, user_id: int,
                  gameplay: str, cerita: str, grafik: str) -> bool:
    """INSERT atau UPDATE review dengan explicit commit."""
    conn = None
    try:
        conn = _conn_write()
        with conn.cursor() as cur:
            # Cek review existing dari user ini untuk game ini
            cur.execute(
                "SELECT id_review FROM review "
                "WHERE id_game = %s AND id_user = %s LIMIT 1",
                (game_id, user_id),
            )
            existing = cur.fetchone()  # DictCursor → dict atau None

            if existing:
                cur.execute(
                    """UPDATE review
                       SET review_gameplay = %s,
                           review_cerita   = %s,
                           review_grafik   = %s
                       WHERE id_review = %s""",
                    (gameplay or None, cerita or None, grafik or None,
                     existing["id_review"]),
                )
                print(f"[submit_review] UPDATE id={existing['id_review']} "
                      f"rows={cur.rowcount}")
            else:
                cur.execute(
                    """INSERT INTO review
                           (id_game, id_user,
                            review_gameplay, review_cerita, review_grafik)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (game_id, user_id,
                     gameplay or None, cerita or None, grafik or None),
                )
                print(f"[submit_review] INSERT lastrowid={cur.lastrowid}")

        conn.commit()
        conn.close()
        return True

    except Exception as exc:
        print(f"[submit_review] Error: {exc}")
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Sinyal worker — selalu dibuat di main thread
# ─────────────────────────────────────────────────────────────────────────────
class _GameDetailSignals(QObject):
    game_ready    = pyqtSignal(object)
    history_ready = pyqtSignal(list)
    genre_ready   = pyqtSignal(list)
    reviews_ready = pyqtSignal(list)
    error         = pyqtSignal(str)


class _FetchGameWorker(QRunnable):
    def __init__(self, game_id, signals: _GameDetailSignals):
        super().__init__()
        self.game_id = game_id
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        print(f"[FetchWorker] mulai fetch game_id={self.game_id}")
        game = fetch_game_by_id(self.game_id)
        if game is None:
            self.signals.error.emit(f"Game id={self.game_id} tidak ditemukan.")
            self.signals.game_ready.emit(None)
            return

        self.signals.game_ready.emit(game)
        self.signals.history_ready.emit(fetch_price_history(self.game_id))
        self.signals.genre_ready.emit(fetch_genres(self.game_id))

        print(f"[FetchWorker] mulai fetch reviews game_id={self.game_id}")
        reviews = fetch_reviews(self.game_id)
        print(f"[FetchWorker] emit reviews_ready, jumlah={len(reviews)}")
        self.signals.reviews_ready.emit(reviews)


class _SubmitReviewSignals(QObject):
    done = pyqtSignal(bool)


class _SubmitReviewWorker(QRunnable):
    def __init__(self, game_id: int, user_id: int,
                 gameplay: str, cerita: str, grafik: str,
                 signals: _SubmitReviewSignals):
        super().__init__()
        self.game_id  = game_id
        self.user_id  = user_id
        self.gameplay = gameplay
        self.cerita   = cerita
        self.grafik   = grafik
        self.signals  = signals
        self.setAutoDelete(True)

    def run(self):
        ok = submit_review(
            self.game_id, self.user_id,
            self.gameplay, self.cerita, self.grafik,
        )
        self.signals.done.emit(ok)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
class GameDetailLoader(QObject):
    game_ready    = pyqtSignal(object)
    history_ready = pyqtSignal(list)
    genre_ready   = pyqtSignal(list)
    reviews_ready = pyqtSignal(list)
    error         = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _GameDetailSignals()
        self._signals.game_ready.connect(self.game_ready)
        self._signals.history_ready.connect(self.history_ready)
        self._signals.genre_ready.connect(self.genre_ready)
        self._signals.reviews_ready.connect(self.reviews_ready)
        self._signals.error.connect(self.error)

    def load(self, game_id):
        worker = _FetchGameWorker(game_id, self._signals)
        QThreadPool.globalInstance().start(worker)


class ReviewSubmitter(QObject):
    done  = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _SubmitReviewSignals()
        self._signals.done.connect(self.done)

    def submit(self, game_id, user_id: int,
               gameplay: str, cerita: str, grafik: str):
        worker = _SubmitReviewWorker(
            game_id, user_id, gameplay, cerita, grafik, self._signals,
        )
        QThreadPool.globalInstance().start(worker)


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
                self.url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.signals.done.emit(resp.read())
        except Exception as e:
            print(f"[ImageFetcher] Error: {e}")
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
# Format helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt_price(price: float) -> str:
    if price == 0:
        return "Gratis"
    return "Rp {:,.0f}".format(price).replace(",", ".")


def fmt_number(n: int) -> str:
    return "{:,}".format(n).replace(",", ".")


def rating_label(rating: int) -> str:
    if rating >= 90: return "Excellent"
    if rating >= 70: return "Good"
    if rating >= 50: return "Mixed"
    return "Negative"


# ─────────────────────────────────────────────────────────────────────────────
# Cek Wishlist
# ─────────────────────────────────────────────────────────────────────────────
def check_wishlist(game_id: str, user_id: int) -> bool:
    """Cek apakah game ada di wishlist user."""
    sql = "SELECT 1 FROM wishlist WHERE id_game = %s AND id_user = %s LIMIT 1"
    try:
        conn = _conn_read()
        with conn.cursor() as cur:
            cur.execute(sql, (game_id, user_id))
            result = cur.fetchone()
        conn.close()
        print(f"[check_wishlist] game_id={game_id}, user_id={user_id}, result={result}")  # ← tambah
        return result is not None
    except Exception as e:
        print(f"[check_wishlist] Error: {e}")
        return False


def toggle_wishlist(game_id: str, user_id: int, add: bool) -> bool:
    """Tambah atau hapus game dari wishlist. Return True jika berhasil."""
    print(f"[toggle_wishlist] game_id={game_id}, user_id={user_id}, add={add}")  # ← tambah ini
    try:
        conn = _conn_write()
        with conn.cursor() as cur:
            if add:
                cur.execute(
                    "INSERT INTO wishlist (id_game, id_user, tanggal_ditambahkan) VALUES (%s, %s, NOW())",
                    (game_id, user_id)
                )
            else:
                cur.execute(
                    "DELETE FROM wishlist WHERE id_game = %s AND id_user = %s",
                    (game_id, user_id)
                )
        conn.commit()
        conn.close()
        print(f"[toggle_wishlist] berhasil")  # ← tambah ini
        return True
    except Exception as e:
        print(f"[toggle_wishlist] Error: {e}")
        return False