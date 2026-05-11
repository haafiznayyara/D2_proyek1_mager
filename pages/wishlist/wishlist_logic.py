# -*- coding: utf-8 -*-
"""
pages/wishlist/wishlist_logic.py
"""

import pymysql
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from pages.wishlist.wishlist_ui import DeleteConfirmDialog


# ── Konfigurasi koneksi database ──────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",
    "database": "mager_db",
    "charset":  "utf8mb4",
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


# ── Fungsi DB ─────────────────────────────────────────────────────────

def fetch_wishlist(id_user: int) -> list:
    sql = """
        SELECT
            w.id_wishlist,
            w.id_game,
            g.nama_game,
            g.url_gambar,
            g.harga_sekarang AS harga_diskon,
            hp.harga_reguler,
            ROUND((1 - hp.harga_diskon / NULLIF(hp.harga_reguler, 0)) * 100) AS persen_diskon,
            ROUND(g.good_review / NULLIF(g.good_review + g.bad_review, 0) * 100) AS rating,
            w.tanggal_ditambahkan,
            GROUP_CONCAT(gr.nama_genre ORDER BY gr.nama_genre SEPARATOR ', ') AS genres
        FROM wishlist w
        JOIN game g ON g.id_game = w.id_game
        LEFT JOIN history_price hp
            ON hp.id_game = g.id_game
            AND hp.id_history = (
                    SELECT MAX(h2.id_history)
                    FROM history_price h2
                    WHERE h2.id_game = g.id_game
                )
        LEFT JOIN detail_genre dg ON dg.id_game = g.id_game
        LEFT JOIN genre gr        ON gr.id_genre = dg.id_genre
        WHERE w.id_user = %s
        GROUP BY w.id_wishlist, w.id_game, g.nama_game,
                hp.harga_reguler, hp.harga_diskon,
                w.tanggal_ditambahkan, g.good_review, g.bad_review
        ORDER BY w.tanggal_ditambahkan DESC
    """
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, (id_user,))
            return cur.fetchall()
    finally:
        conn.close()

def add_to_wishlist(id_user: int, id_game: str) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Cek duplikat dulu
            cur.execute(
                "SELECT 1 FROM wishlist WHERE id_user = %s AND id_game = %s",
                (id_user, id_game)
            )
            if cur.fetchone():
                return "duplicate"
            cur.execute(
                "INSERT INTO wishlist (id_user, id_game, tanggal_ditambahkan) VALUES (%s, %s, NOW())",
                (id_user, id_game)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Gagal tambah wishlist: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_wishlist_item(id_wishlist: int) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM wishlist WHERE id_wishlist = %s", (id_wishlist,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Gagal hapus wishlist id={id_wishlist}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def count_wishlist(id_user: int) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM wishlist WHERE id_user = %s",
                (id_user,)
            )
            result = cur.fetchone()
            return result[0] if result else 0
    finally:
        conn.close()

# ── Logic class ───────────────────────────────────────────────────────

class WishlistLogic(QObject):
    go_to_dashboard = pyqtSignal()
    wishlist_count_changed = pyqtSignal(int)

    def __init__(self, ui, id_user: int, parent=None):
        super().__init__(parent)
        self.ui      = ui
        self.id_user = id_user

        self._connect_static_nav()
        self.load_wishlist()

    def _connect_static_nav(self):
        for btn_name in ("btnKembali", "btnJelajahiGame2"):
            btn = getattr(self.ui, btn_name, None)
            if btn is not None:
                btn.clicked.connect(self._on_jelajahi_clicked)

    def _connect_cta_nav(self):
        btn = getattr(self.ui, "btnJelajahiGame1", None)
        if btn is not None:
            try:
                btn.clicked.disconnect(self._on_jelajahi_clicked)
            except TypeError:
                pass
            btn.clicked.connect(self._on_jelajahi_clicked)

    def _on_jelajahi_clicked(self):
        self.go_to_dashboard.emit()

    def load_wishlist(self):
        items = fetch_wishlist(self.id_user)
        if hasattr(self.ui, "render_wishlist"):
            self.ui.render_wishlist(items)
        self._connect_cta_nav()
        self._update_subtitle(len(items))
        self.wishlist_count_changed.emit(len(items))

    def _update_subtitle(self, jumlah: int):
        label = getattr(self.ui, "subtitleLabel", None)
        if label is None:
            return
        if jumlah == 0:
            label.setText("Wishlist Anda masih kosong")
        else:
            label.setText(f"Anda memiliki {jumlah} game dalam wishlist")

    def on_delete_clicked(self, id_wishlist: int, nama_game: str):
        """Tampilkan custom dialog konfirmasi lalu hapus jika dikonfirmasi."""
        dialog = DeleteConfirmDialog(nama_game, parent=self.ui)
        dialog.exec_()

        if not dialog.confirmed():
            return

        success = delete_wishlist_item(id_wishlist)
        if success:
            self.load_wishlist()
        else:
            QMessageBox.critical(
                self.ui,
                "Gagal",
                "Terjadi kesalahan saat menghapus item.\nSilakan coba lagi.",
            )
    def on_add_clicked(self, game: dict):
        id_game = game.get("id")
        result = add_to_wishlist(self.id_user, id_game)
        if result == "duplicate":
            QMessageBox.information(
                self.ui, "Info",
                f"<b>{game.get('title')}</b> sudah ada di wishlist kamu!"
            )
        elif result:
            QMessageBox.information(
                self.ui, "Berhasil",
                f"<b>{game.get('title')}</b> berhasil ditambahkan ke wishlist!"
            )
        else:
            QMessageBox.critical(
                self.ui, "Gagal",
                "Terjadi kesalahan. Silakan coba lagi."
            )