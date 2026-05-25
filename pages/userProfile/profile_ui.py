# -*- coding: utf-8 -*-
"""
pages/userProfile/profile_ui.py
Tampilan halaman Profile User — hanya UI, tanpa logic/DB.
"""

import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QPushButton, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from widget.navbar import Navbar
from pages.userProfile.crop_dialog import CropDialog
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QIcon
from PyQt5.QtCore import QSize, Qt, QRect

STYLESHEET = """
QMainWindow {
    background-color: #0A1123;
}
QWidget#centralwidget {
    background-color: #0A1123;
}

/* ===== BACK BUTTON ===== */
QPushButton#btnBack {
    color: #8B96A5;
    font-size: 13px;
    font-family: 'Segoe UI';
    background: transparent;
    border: none;
    text-align: left;
    padding: 4px 0px;
}
QPushButton#btnBack:hover {
    color: #FFFFFF;
}

/* ===== LEFT PANEL ===== */
QWidget#leftPanel {
    background-color: #1A2332;
    border-radius: 12px;
}
QLabel#panelTitle {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Segoe UI';
}
QLabel#fieldLabel, QLabel#fieldLabel_2 {
    color: #8B96A5;
    font-size: 11px;
    font-family: 'Segoe UI';
}
QLineEdit#displayNameEdit {
    background-color: #1A1F36;
    border: 1px solid #2A3050;
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 13px;
    font-family: 'Segoe UI';
    padding: 6px 10px;
}
QLineEdit#usernameEdit {
    background-color: transparent;
    border: 1px solid #2A3050;
    border-radius: 6px;
    color: #8B96A5;
    font-size: 13px;
    font-family: 'Segoe UI';
    padding: 6px 10px;
}
QPushButton#btnSave {
    background-color: #4ADE80;
    color: #0F1621;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnSave:hover {
    background-color: #16a34a;
}
QLabel#sectionLabel {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    font-family: 'Segoe UI';
}
QLabel#emptyLabel {
    color: #515050;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QPushButton#btnLogout {
    background-color: #5c1a1a;
    color: #e05555;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnLogout:hover {
    background-color: #701f1f;
}

/* ===== RIGHT CARDS ===== */
QWidget#cardLike, QWidget#cardDislike, QWidget#cardKomentar, QWidget#cardWishlist {
    background-color: #1A2332;
    border-radius: 12px;
}
QLabel#cardTotal {
    color: #8B96A5;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QLabel#cardEmpty, QLabel#cardLikeEmpty, QLabel#cardDislikeEmpty,
QLabel#cardKomentarEmpty {
    color: #515050;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QPushButton#btnWishlist {
    background-color: #4ADE80;
    color: #0F1621;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnWishlist:hover {
    background-color: #16a34a;
}
"""


def icon_path(filename):
    """Resolve path ikon dari folder assets."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "..", "assets", filename)


def make_icon_label(png_file, size=20):
    """Buat QLabel yang menampilkan ikon PNG dengan ukuran tetap."""
    lbl = QtWidgets.QLabel()
    lbl.setFixedSize(size, size)
    lbl.setScaledContents(True)
    lbl.setPixmap(QtGui.QPixmap(icon_path(png_file)))
    return lbl

class GenreBarChart(QtWidgets.QWidget):
    """Bar chart horizontal untuk 5 genre favorit user."""

    BAR_COLOR     = QColor("#4ADE80")
    BAR_BG_COLOR  = QColor("#0d1829")
    TEXT_COLOR    = QColor("#c9d1e0")
    MUTED_COLOR   = QColor("#7b8db0")
    EMPTY_COLOR   = QColor("#515050")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[dict] = []   # [{'nama_genre': str, 'total': int}]
        self.setMinimumHeight(180)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )
        self.setStyleSheet("background: transparent;")

    def set_data(self, genres: list[dict]):
        """genres = [{'nama_genre': str, 'total': int}, ...] max 5."""
        self._data = genres[:5]
        # Tinggi menyesuaikan jumlah bar
        row_h = 36
        self.setMinimumHeight(max(160, len(self._data) * row_h + 40))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 110, 50, 10, 10
        draw_w = W - pad_l - pad_r
        n = len(self._data)

        if n == 0:
            p.setPen(QPen(self.EMPTY_COLOR))
            p.setFont(QFont("Segoe UI", 10))
            p.drawText(
                QRect(0, 0, W, H),
                Qt.AlignCenter,
                "Belum ada data genre favorit"
            )
            return

        max_val = max(d["total"] for d in self._data) or 1
        row_h   = (H - pad_t - pad_b) // n

        for i, item in enumerate(self._data):
            genre = item["nama_genre"] or "—"
            total = int(item["total"])
            y     = pad_t + i * row_h

            # ── Label genre (kiri) ─────────────────────────────────
            p.setPen(QPen(self.TEXT_COLOR))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(
                QRect(0, y + 2, pad_l - 10, row_h - 4),
                Qt.AlignRight | Qt.AlignVCenter,
                genre
            )

            # ── Background bar ─────────────────────────────────────
            bar_h  = max(14, row_h - 16)
            bar_y  = y + (row_h - bar_h) // 2
            p.setBrush(QBrush(self.BAR_BG_COLOR))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(pad_l, bar_y, draw_w, bar_h, 4, 4)

            # ── Foreground bar (fill sesuai nilai) ─────────────────
            fill_w = max(8, int(total / max_val * draw_w))
            p.setBrush(QBrush(self.BAR_COLOR))
            p.drawRoundedRect(pad_l, bar_y, fill_w, bar_h, 4, 4)

            # ── Angka di kanan bar ─────────────────────────────────
            p.setPen(QPen(self.MUTED_COLOR))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(
                QRect(pad_l + draw_w + 6, y + 2, pad_r - 6, row_h - 4),
                Qt.AlignLeft | Qt.AlignVCenter,
                str(total)
            )

class ProfileWindow(QtWidgets.QMainWindow):

    # ── Signals ───────────────────────────────────────────────────────
    wishlist_clicked = QtCore.pyqtSignal()
    back_clicked     = QtCore.pyqtSignal()
    logout_clicked   = QtCore.pyqtSignal()
    photo_changed    = QtCore.pyqtSignal(str)   # membawa path foto asli
    save_requested   = QtCore.pyqtSignal(str)   # membawa username baru
    game_detail_requested = QtCore.pyqtSignal(int)   # membawa ID game

    # ── Metode publik (dipanggil dari logic/router) ───────────────────
    def _resolve_photo_path(self, foto_profil: str) -> str:
        """Ubah nama file foto menjadi full path."""
        if not foto_profil:
            return ""
        # Jika sudah berupa path absolut (data lama), biarkan
        if os.path.isabs(foto_profil):
            return foto_profil
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "..", "..", "assets", "profile_photos", foto_profil)

    def load_user(self, user: dict):
        username     = user.get("username", "")
        display_name = user.get("display_name") or username  # fallback ke username
        self.displayNameEdit.setText(display_name)
        self.usernameEdit.setText(username)
        foto = user.get("foto_profil") or ""
        self._current_photo = self._resolve_photo_path(foto)
        if self._current_photo and os.path.exists(self._current_photo):
            self.update_photo(self._current_photo)
        else:
            self.avatarLabel.setPixmap(QtGui.QPixmap())
            self.avatarLabel.setText(display_name[0].upper() if display_name else "?")

    def update_photo(self, path: str):
        """Tampilkan foto profil berbentuk lingkaran."""
        self._current_photo = path
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            return
        pixmap = pixmap.scaled(
            100, 100,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        rounded = QtGui.QPixmap(100, 100)
        rounded.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(pixmap))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, 100, 100)
        painter.end()
        self.avatarLabel.setPixmap(rounded)
        self.avatarLabel.setText("")

    # ── Slot internal ─────────────────────────────────────────────────

    def _on_save_clicked(self):
        new_display = self.displayNameEdit.text().strip()
        if not new_display:
            return
        if not getattr(self, '_current_photo', ''):
            self.avatarLabel.setText(new_display[0].upper())
        self.save_requested.emit(new_display)   

    def _on_photo_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto Profil", "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if not path:
            return
        dialog = CropDialog(path, parent=self)
        dialog.exec_()
        result = dialog.get_result()
        if result:
            self.avatarLabel.setPixmap(
                result.scaled(
                    100, 100,
                    QtCore.Qt.KeepAspectRatioByExpanding,
                    QtCore.Qt.SmoothTransformation
                )
            )
            self.avatarLabel.setText("")
            self._current_photo = path
            self.photo_changed.emit(path)   # ← kirim ke logic

    # ── Constructor ───────────────────────────────────────────────────

    def __init__(self):
        super().__init__()
        self._current_photo = ""
        self.setObjectName("ProfileWindow")
        self.resize(1100, 700)
        self.setWindowTitle("MAGER - Profil User")
        self.setStyleSheet(STYLESHEET)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        self.mainVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)

        # Navbar
        self.nav = Navbar(active_page="profile")
        self.mainVLayout.addWidget(self.nav)

        # Content
        self.contentWidget = QtWidgets.QWidget()
        contentVLayout = QtWidgets.QVBoxLayout(self.contentWidget)
        contentVLayout.setContentsMargins(24, 8, 24, 24)
        contentVLayout.setSpacing(16)

        # Back button
        self.btnBack = QPushButton(" Kembali")
        self.btnBack.setIcon(QIcon("assets/icon-back.png"))
        self.btnBack.setIconSize(QSize(16, 16))
        self.btnBack.setObjectName("btnBack")
        self.btnBack.setMaximumWidth(120)
        self.btnBack.clicked.connect(self.back_clicked.emit)
        contentVLayout.addWidget(self.btnBack)

        mainContentLayout = QtWidgets.QHBoxLayout()
        mainContentLayout.setSpacing(16)
        mainContentLayout.setAlignment(QtCore.Qt.AlignTop)
        mainContentLayout.setContentsMargins(0, 0, 0, 0)

        # ── Left Panel ────────────────────────────────────────────────
        self.leftPanel = QtWidgets.QWidget()
        self.leftPanel.setObjectName("leftPanel")
        self.leftPanel.setMinimumWidth(420)
        self.leftPanel.setMinimumWidth(600)
        self.leftPanel.setMinimumHeight(480)
        self.leftPanel.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding
        )

        leftPanelLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        leftPanelLayout.setContentsMargins(20, 20, 20, 20)
        leftPanelLayout.setSpacing(12)

        self.panelTitle = QtWidgets.QLabel("Profil Saya")
        self.panelTitle.setObjectName("panelTitle")
        leftPanelLayout.addWidget(self.panelTitle)

        # Avatar + tombol kamera
        avatarLayout = QtWidgets.QHBoxLayout()
        avatarLayout.addStretch()

        avatarContainer = QtWidgets.QWidget()
        avatarContainer.setFixedSize(110, 110)
        avatarContainer.setStyleSheet("background: transparent;")

        self.avatarLabel = QtWidgets.QLabel("D", avatarContainer)
        self.avatarLabel.setObjectName("avatarLabel")
        self.avatarLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.avatarLabel.setGeometry(0, 0, 100, 100)
        self.avatarLabel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.avatarLabel.mousePressEvent = lambda _: self._on_photo_clicked()
        self.avatarLabel.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 36px;
                font-weight: bold;
                font-family: 'Segoe UI';
                background-color: #2A3647;
                border-radius: 50px;
            }
        """)

        self.cameraBtn = QtWidgets.QPushButton(avatarContainer)
        self.cameraBtn.setGeometry(72, 72, 30, 30)
        self.cameraBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cameraBtn.setIcon(QtGui.QIcon(icon_path("mdi_camera-outline.png")))
        self.cameraBtn.setIconSize(QtCore.QSize(16, 16))
        self.cameraBtn.setStyleSheet("""
            QPushButton {
                background-color: #4ADE80;
                border-radius: 15px;
                border: 2px solid #0A1123;
                padding: 0px;
            }
            QPushButton:hover { background-color: #16a34a; }
        """)
        self.cameraBtn.clicked.connect(self._on_photo_clicked)
        self.cameraBtn.raise_()

        avatarLayout.addWidget(avatarContainer)
        avatarLayout.addStretch()
        leftPanelLayout.addLayout(avatarLayout)

        # Display Name (editable)
        self.fieldLabel = QtWidgets.QLabel("Display Name")
        self.fieldLabel.setObjectName("fieldLabel")
        self.displayNameEdit = QtWidgets.QLineEdit()
        self.displayNameEdit.setObjectName("displayNameEdit")
        self.displayNameEdit.setReadOnly(False)
        leftPanelLayout.addWidget(self.fieldLabel)
        leftPanelLayout.addWidget(self.displayNameEdit)

        # Username (read only)
        self.fieldLabel_2 = QtWidgets.QLabel("Username")
        self.fieldLabel_2.setObjectName("fieldLabel_2")
        self.usernameEdit = QtWidgets.QLineEdit()
        self.usernameEdit.setObjectName("usernameEdit")
        self.usernameEdit.setReadOnly(True)
        leftPanelLayout.addWidget(self.fieldLabel_2)
        leftPanelLayout.addWidget(self.usernameEdit)

        # Simpan
        self.btnSave = QtWidgets.QPushButton("Simpan Perubahan")
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self._on_save_clicked)
        leftPanelLayout.addWidget(self.btnSave)

        # Statistik
        self.sectionLabel = QtWidgets.QLabel("Statistik Preferensi")
        self.sectionLabel.setObjectName("sectionLabel")
        leftPanelLayout.addWidget(self.sectionLabel)

        # Bar chart widget
        self.genreChart = GenreBarChart()
        leftPanelLayout.addWidget(self.genreChart)

        # Logout
        self.btnLogout = QtWidgets.QPushButton("  Logout")
        self.btnLogout.setObjectName("btnLogout")
        self.btnLogout.setIcon(QtGui.QIcon(icon_path("material-symbols_logout-rounded.png")))
        self.btnLogout.setIconSize(QtCore.QSize(18, 18))
        self.btnLogout.clicked.connect(self._on_logout_clicked)
        leftPanelLayout.addWidget(self.btnLogout)

        mainContentLayout.addWidget(self.leftPanel, 1)

        # ── Right Panel — 2×2 card grid ──────────────────────────────
        cardsGridLayout = QtWidgets.QGridLayout()
        cardsGridLayout.setSpacing(12)
        cardsGridLayout.setVerticalSpacing(12)

        def make_card(obj_name, icon_png, title_text, title_color,
                      total_text, empty_text, extra_widget=None):
            card = QtWidgets.QWidget()
            card.setObjectName(obj_name)
            card.setMinimumHeight(250)
            vbox = QtWidgets.QVBoxLayout(card)
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(8)

            title_row = QtWidgets.QHBoxLayout()
            title_row.setSpacing(8)
            title_row.addWidget(make_icon_label(icon_png, 20))
            title_lbl = QtWidgets.QLabel(title_text)
            title_lbl.setStyleSheet(
                f"color: {title_color}; font-size: 16px; font-weight: bold; font-family: 'Segoe UI';"
            )
            title_row.addWidget(title_lbl)
            title_row.addStretch()
            vbox.addLayout(title_row)

            total_lbl = QtWidgets.QLabel(total_text)
            total_lbl.setStyleSheet("color: #8B96A5; font-size: 12px; font-family: 'Segoe UI';")
            vbox.addWidget(total_lbl)

            vbox.addStretch()

            empty_lbl = QtWidgets.QLabel(empty_text)
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
            vbox.addWidget(empty_lbl)

            vbox.addStretch()

            if extra_widget:
                vbox.addWidget(extra_widget)

            return card

        def make_list_card(obj_name, icon_png, title_text, empty_text):
            card = QtWidgets.QWidget()
            card.setObjectName(obj_name)
            card.setMinimumHeight(250)
            card.setMaximumHeight(250)
            vbox = QtWidgets.QVBoxLayout(card)
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(8)

            title_row = QtWidgets.QHBoxLayout()
            title_row.setSpacing(8)
            title_row.addWidget(make_icon_label(icon_png, 20))
            title_lbl = QtWidgets.QLabel(title_text)
            title_lbl.setStyleSheet(
                "color: #FFFFFF; font-size: 16px; font-weight: bold; font-family: 'Segoe UI';"
            )
            title_row.addWidget(title_lbl)
            title_row.addStretch()
            vbox.addLayout(title_row)

            total_lbl = QtWidgets.QLabel("Total: 0 Game")
            total_lbl.setStyleSheet("color: #8B96A5; font-size: 12px; font-family: 'Segoe UI';")
            vbox.addWidget(total_lbl)

            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet("""
                QScrollArea { background: transparent; border: none; }
                QScrollBar:vertical { background: #0d1829; width: 5px; border-radius: 2px; }
                QScrollBar::handle:vertical { background: #2A3647; border-radius: 2px; }
                QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
            """)

            container = QtWidgets.QWidget()
            container.setStyleSheet("background: transparent;")
            list_layout = QtWidgets.QVBoxLayout(container)
            list_layout.setContentsMargins(0, 0, 0, 0)
            list_layout.setSpacing(4)

            empty_lbl = QtWidgets.QLabel(empty_text)
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
            list_layout.addWidget(empty_lbl)
            list_layout.addStretch()

            scroll.setWidget(container)
            vbox.addWidget(scroll)

            card._total_lbl   = total_lbl
            card._list_layout = list_layout
            card._empty_text  = empty_text
            return card

        self.cardLike     = make_list_card("cardLike",     "Vector.png",       "Riwayat Like",     "Belum ada game yang di-like")
        self.cardDislike  = make_list_card("cardDislike",  "Vector (2).png",   "Riwayat Dislike",  "Belum ada game yang di-dislike")
        self.cardKomentar = make_list_card("cardKomentar", "Vector (1).png",   "Riwayat Komentar", "Belum ada komentar")

        self.btnWishlist = QtWidgets.QPushButton("Lihat Wishlist")
        self.btnWishlist.setObjectName("btnWishlist")
        self.btnWishlist.setFixedHeight(36)
        self.btnWishlist.clicked.connect(self.wishlist_clicked.emit)
        self.btnWishlist.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.cardWishlist = make_card(
            "cardWishlist", "Vector (3).png", "Riwayat Wishlist", "#FFFFFF",
            "Total: 0 Game", "", extra_widget=self.btnWishlist
        )

        cardsGridLayout.addWidget(self.cardLike,     0, 0)
        cardsGridLayout.addWidget(self.cardDislike,  0, 1)
        cardsGridLayout.addWidget(self.cardKomentar, 1, 0)
        cardsGridLayout.addWidget(self.cardWishlist, 1, 1)

        # Bungkus cardsGridLayout dengan widget agar bisa dibatasi
        cardsWidget = QtWidgets.QWidget()
        cardsWidget.setLayout(cardsGridLayout)
        cardsWidget.setContentsMargins(0, 0, 0, 0)
        cardsGridLayout.setContentsMargins(0, 0, 0, 0)
        cardsGridLayout.setColumnStretch(0, 1)
        cardsGridLayout.setColumnStretch(1, 1)
        mainContentLayout.addWidget(cardsWidget, 3, QtCore.Qt.AlignTop)

        contentVLayout.addLayout(mainContentLayout)
        self.mainVLayout.addWidget(self.contentWidget)

    def load_genre_chart(self, genres: list[dict]):
        self.genreChart.set_data(genres)
        
    def update_like_dislike_count(self, like: int, dislike: int):
        for lbl in self.cardLike.findChildren(QtWidgets.QLabel):
            if lbl.text().startswith("Total:"):
                lbl.setText(f"Total: {like} Game")
                break
        for lbl in self.cardDislike.findChildren(QtWidgets.QLabel):
            if lbl.text().startswith("Total:"):
                lbl.setText(f"Total: {dislike} Game")
                break
    def update_like_dislike_list(self, games: list[dict]):
        def _fill_card(card, items):
            layout = card._list_layout
            # Hapus semua kecuali empty label dan stretch
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            card._total_lbl.setText(f"Total: {len(items)} Game")

            if not items:
                empty = QtWidgets.QLabel(
                    "Belum ada game yang di-like" if "Like" in card._total_lbl.parent().objectName()
                    else "Belum ada game yang di-dislike"
                )
                empty.setAlignment(QtCore.Qt.AlignCenter)
                empty.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
                layout.addWidget(empty)
            else:
                for g in items:
                    row = QtWidgets.QWidget()
                    row.setStyleSheet("background: #0d1829; border-radius: 6px;")
                    rh = QtWidgets.QHBoxLayout(row)
                    rh.setContentsMargins(10, 7, 10, 7)
                    name_lbl = QtWidgets.QLabel(g["nama_game"])
                    name_lbl.setStyleSheet("color: #c9d1e0; font-size: 12px; font-family: 'Segoe UI'; background: transparent;")
                    icon_lbl = QtWidgets.QLabel()
                    icon_lbl.setFixedSize(18, 18)
                    icon_lbl.setScaledContents(True)
                    icon_lbl.setPixmap(QtGui.QPixmap(icon_path("Vector.png" if g["type"] == "like" else "Vector (2).png")))
                    icon_lbl.setStyleSheet("background: transparent;")
                    rh.addWidget(name_lbl)
                    rh.addStretch()
                    rh.addWidget(icon_lbl)
                    layout.addWidget(row)

            layout.addStretch()

        liked    = [g for g in games if g["type"] == "like"]
        disliked = [g for g in games if g["type"] == "dislike"]
        _fill_card(self.cardLike,    liked)
        _fill_card(self.cardDislike, disliked)
    
    def update_review_list(self, reviews: list[dict]):
        layout = self.cardKomentar._list_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cardKomentar._total_lbl.setText(f"Total: {len(reviews)} Game")

        if not reviews:
            empty = QtWidgets.QLabel("Belum ada komentar")
            empty.setAlignment(QtCore.Qt.AlignCenter)
            empty.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
            layout.addWidget(empty)
        else:
            for r in reviews:
                row = QtWidgets.QWidget()
                row.setStyleSheet("background: #0d1829; border-radius: 6px;")
                rv = QtWidgets.QVBoxLayout(row)
                rv.setContentsMargins(10, 8, 10, 8)
                rv.setSpacing(3)

                name_lbl = QtWidgets.QLabel(r["nama_game"])
                name_lbl.setStyleSheet(
                    "color: #4ADE80; font-size: 12px; font-weight: bold; font-family: 'Segoe UI'; background: transparent;"
                )
                rv.addWidget(name_lbl)

                # Ambil teks review pertama yang tidak kosong
                preview = (
                    r.get("review_gameplay") or
                    r.get("review_cerita") or
                    r.get("review_grafik") or ""
                ).strip()
                if len(preview) > 60:
                    preview = preview[:60] + "..."

                if preview:
                    text_lbl = QtWidgets.QLabel(preview)
                    text_lbl.setStyleSheet(
                        "color: #7b8db0; font-size: 11px; font-family: 'Segoe UI'; background: transparent;"
                    )
                    rv.addWidget(text_lbl)

                layout.addWidget(row)
        layout.addStretch()
    
    # Alert dialog untuk konfirmasi logout
    def _on_logout_clicked(self):
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setModal(True)
        dialog.setFixedWidth(400)

    def update_wishlist_count(self, jumlah: int):
        """Update label total game di card Riwayat Wishlist."""
        for lbl in self.cardWishlist.findChildren(QtWidgets.QLabel):
            if lbl.text().startswith("Total:"):
                lbl.setText(f"Total: {jumlah} Game")
                break

    def update_like_dislike_list(self, games: list[dict]):
        """Isi card Like dan Dislike dengan list game."""
        liked    = [g for g in games if g["type"] == "like"]
        disliked = [g for g in games if g["type"] == "dislike"]

        def _fill(card, items, icon_file, empty_text):
            layout = card._list_layout
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            card._total_lbl.setText(f"Total: {len(items)} Game")

            if not items:
                lbl = QtWidgets.QLabel(empty_text)
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                lbl.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
                layout.addWidget(lbl)
            else:
                for g in items:
                    row = QtWidgets.QWidget()
                    row.setStyleSheet("background: #0d1829; border-radius: 6px; border: none; ")
                    row.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                    rh = QtWidgets.QHBoxLayout(row)
                    rh.setContentsMargins(10, 7, 10, 7)
                    name_lbl = QtWidgets.QLabel(g["nama_game"])
                    name_lbl.setStyleSheet("color: #c9d1e0; font-size: 12px; font-family: 'Segoe UI'; background: transparent;")
                    ico = QtWidgets.QLabel()
                    ico.setFixedSize(16, 16)
                    ico.setScaledContents(True)
                    ico.setPixmap(QtGui.QPixmap(icon_path(icon_file)))
                    ico.setStyleSheet("background: transparent;")
                    rh.addWidget(name_lbl)
                    rh.addStretch()
                    rh.addWidget(ico)
                    _gid = g["id_game"]
                    row.mousePressEvent = lambda _, gid=_gid: self.game_detail_requested.emit(gid)
                    row.enterEvent      = lambda _, r=row: r.setStyleSheet("background: #0d1829; border-radius: 6px; border: none; ")
                    row.leaveEvent      = lambda _, r=row: r.setStyleSheet("background: #0d1829; border-radius: 6px; border: none; ")
                    layout.addWidget(row)
            layout.addStretch()

        _fill(self.cardLike,    liked,    "Vector.png",     "Belum ada game yang di-like")
        _fill(self.cardDislike, disliked, "Vector (2).png", "Belum ada game yang di-dislike")

    def update_review_list(self, reviews: list[dict]):
        """Isi card Komentar dengan list review."""
        layout = self.cardKomentar._list_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cardKomentar._total_lbl.setText(f"Total: {len(reviews)} Game")

        if not reviews:
            lbl = QtWidgets.QLabel("Belum ada komentar")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
            layout.addWidget(lbl)
        else:
            for r in reviews:
                row = QtWidgets.QWidget()
                row.setStyleSheet("background: #0d1829; border-radius: 6px; border: none;")
                row.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                rv = QtWidgets.QVBoxLayout(row)
                rv.setContentsMargins(10, 8, 10, 8)
                rv.setSpacing(3)
                name_lbl = QtWidgets.QLabel(r["nama_game"])
                name_lbl.setStyleSheet("color: #4ADE80; font-size: 12px; font-weight: bold; font-family: 'Segoe UI'; background: transparent;")
                rv.addWidget(name_lbl)
                preview = (r.get("review_gameplay") or r.get("review_cerita") or r.get("review_grafik") or "").strip()
                if len(preview) > 60:
                    preview = preview[:60] + "..."
                if preview:
                    text_lbl = QtWidgets.QLabel(preview)
                    text_lbl.setStyleSheet("color: #7b8db0; font-size: 11px; font-family: 'Segoe UI'; background: transparent;")
                    rv.addWidget(text_lbl)
                _gid = r["id_game"]
                row.mousePressEvent = lambda _, gid=_gid: self.game_detail_requested.emit(gid)
                row.enterEvent      = lambda _, rw=row: rw.setStyleSheet("background: #0d1829; border-radius: 6px; border: none;")
                row.leaveEvent      = lambda _, rw=row: rw.setStyleSheet("background: #0d1829; border-radius: 6px; border: none;")
                layout.addWidget(row)
        layout.addStretch()


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ProfileWindow()
    window.show()
    sys.exit(app.exec_())