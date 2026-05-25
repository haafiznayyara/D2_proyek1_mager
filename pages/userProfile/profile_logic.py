# -*- coding: utf-8 -*-
"""
pages/userProfile/profile_logic.py
Logic layer untuk halaman Profile User.
"""

import os
import shutil
import pymysql
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

# ── Konfigurasi DB ────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",           
    "database": "mager_db",
    "autocommit": True,
}
DB_PORTS = [3306, 3307]

def get_connection():
    """Coba koneksi ke beberapa port MySQL menggunakan PyMySQL."""
    for port in DB_PORTS:
        try:
            conn = pymysql.connect(
                **DB_CONFIG,
                port=port
            )
            print(f"[DB Profile] Connected to MySQL port {port}")
            return conn
        except Exception as e: 
            print(f"[DB Profile] Failed port {port} -> {e}")

    raise Exception("Tidak bisa terhubung ke MySQL di port 3306 maupun 3307")

# Folder penyimpanan foto profil
BASE_DIR         = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFILE_PHOTO_DIR = os.path.join(BASE_DIR, "assets", "profile_photos")

# ── Fungsi DB ─────────────────────────────────────────────────────────

def fetch_user(id_user: int) -> dict:
    """Ambil data user dari DB berdasarkan id_user."""
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT id_user, username, display_name, foto_profil FROM users WHERE id_user = %s",
                (id_user,)
            )
            return cur.fetchone() or {}
    finally:
        conn.close()
        
def fetch_favorite_genres(id_user: int) -> list[dict]:
    """
    Ambil 5 genre teratas berdasarkan game yang di-like user.
    Return: [{'nama_genre': str, 'total': int}, ...]
    """
    sql = """
        SELECT g.nama_genre, COUNT(*) AS total
        FROM game_likes gl
        JOIN detail_genre dg ON gl.id_game = dg.id_game
        JOIN genre g ON dg.id_genre = g.id_genre
        WHERE gl.id_user = %s AND gl.type = 'like'
        GROUP BY g.nama_genre
        ORDER BY total DESC
        LIMIT 5
    """
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, (id_user,))
            return cur.fetchall() or []
    except Exception as e:
        print(f"[fetch_favorite_genres] Error: {e}")
        return []
    finally:
        conn.close()


def fetch_liked_games(id_user: int) -> list[dict]:
    """Ambil semua game yang di-like/dislike user."""
    sql = """
        SELECT g.id_game, g.nama_game, gl.type
        FROM game_likes gl
        JOIN game g ON gl.id_game = g.id_game
        WHERE gl.id_user = %s
    """
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, (id_user,))
            return cur.fetchall() or []
    except Exception as e:
        print(f"[fetch_liked_games] Error: {e}")
        return []
    finally:
        conn.close()


def fetch_user_reviews(id_user: int) -> list[dict]:
    """Ambil semua review yang ditulis user."""
    sql = """
        SELECT g.id_game, g.nama_game, r.review_gameplay, r.review_cerita, r.review_grafik
        FROM review r
        JOIN game g ON r.id_game = g.id_game
        WHERE r.id_user = %s
        ORDER BY r.id_review DESC
    """
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, (id_user,))
            return cur.fetchall() or []
    except Exception as e:
        print(f"[fetch_user_reviews] Error: {e}")
        return []
    finally:
        conn.close()


def update_display_name(id_user: int, display_name: str) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET display_name = %s WHERE id_user = %s",
                (display_name, id_user)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Gagal update display_name: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_foto_profil(id_user: int, src_path: str) -> str | None:
    """
    Salin foto dari src_path ke folder assets/profile_photos,
    lalu simpan path-nya ke DB.
    Kembalikan path baru jika berhasil, None jika gagal.
    """
    # Buat folder jika belum ada
    os.makedirs(PROFILE_PHOTO_DIR, exist_ok=True)

    # Nama file unik berdasarkan id_user
    ext      = os.path.splitext(src_path)[1]
    filename = f"user_{id_user}{ext}"
    dst_path = os.path.join(PROFILE_PHOTO_DIR, filename)

    try:
        shutil.copy2(src_path, dst_path)
    except Exception as e:
        print(f"[ERROR] Gagal salin foto: {e}")
        return None

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET foto_profil = %s WHERE id_user = %s",
                (filename, id_user)
            )
        conn.commit()
        return filename
    except Exception as e:
        print(f"[ERROR] Gagal update foto_profil di DB: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


# ── Logic Class ───────────────────────────────────────────────────────

def fetch_wishlist_count(id_user: int) -> int:
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM wishlist WHERE id_user = %s", (id_user,))
            return cur.fetchone()[0] or 0
    except Exception as e:
        print(f"[fetch_wishlist_count] Error: {e}")
        return 0
    finally:
        conn.close()


class ProfileLogic(QObject):
    """
    Logic layer Profile.

    Signals
    -------
    username_updated : pyqtSignal(str)
        Dipancarkan setelah username berhasil diupdate di DB.
    photo_saved : pyqtSignal(str)
        Dipancarkan setelah foto berhasil disimpan, membawa path baru.
    """

    username_updated = pyqtSignal(str)
    photo_saved      = pyqtSignal(str)

    def __init__(self, ui, id_user: int, parent=None):
        super().__init__(parent)
        self.photo_saved.connect(
            lambda filename: self.ui.update_photo(
                os.path.join(PROFILE_PHOTO_DIR, filename)
            )
        )
        self.ui      = ui
        self.id_user = id_user

        # Sambungkan sinyal dari UI ke logic
        self.ui.save_requested.connect(self.on_save_display_name)
        self.ui.photo_changed.connect(self.on_photo_changed)

        # Load data user terbaru dari DB
        self._load_user()

    def _load_user(self):
        """Ambil data user dari DB dan tampilkan ke UI."""
        user = fetch_user(self.id_user)
        if user:
            self.ui.load_user(user)

        genres = fetch_favorite_genres(self.id_user)
        self.ui.load_genre_chart(genres)

        games = fetch_liked_games(self.id_user)
        self.ui.update_like_dislike_list(games)

        reviews = fetch_user_reviews(self.id_user)
        self.ui.update_review_list(reviews)

        wishlist_count = fetch_wishlist_count(self.id_user)
        self.ui.update_wishlist_count(wishlist_count)

    def refresh(self):
        self._load_user()

    def on_save_display_name(self, new_display: str):
        if not new_display:
            return
        success = update_display_name(self.id_user, new_display)
        if success:
            self.username_updated.emit(new_display)
            QMessageBox.information(
                self.ui, "Berhasil",
                f"Display Name berhasil diubah menjadi <b>{new_display}</b>!"
            )
        else:
            QMessageBox.critical(
                self.ui, "Gagal",
                "Terjadi kesalahan saat menyimpan.\nSilakan coba lagi."
            )

    def on_photo_changed(self, src_path: str):
        """Dipanggil saat user memilih foto baru."""
        new_path = update_foto_profil(self.id_user, src_path)
        if new_path:
            self.photo_saved.emit(new_path)
        else:
            QMessageBox.critical(
                self.ui, "Gagal",
                "Terjadi kesalahan saat menyimpan foto.\nSilakan coba lagi."
            )