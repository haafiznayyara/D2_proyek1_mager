# -*- coding: utf-8 -*-
"""
pages/userProfile/profile_ui.py
Tampilan halaman Profile User — hanya UI, tanpa logic/DB.
"""

import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from widget.navbar import Navbar
from pages.userProfile.crop_dialog import CropDialog

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


class ProfileWindow(QtWidgets.QMainWindow):

    # ── Signals ───────────────────────────────────────────────────────
    wishlist_clicked = QtCore.pyqtSignal()
    back_clicked     = QtCore.pyqtSignal()
    logout_clicked   = QtCore.pyqtSignal()
    photo_changed    = QtCore.pyqtSignal(str)   # membawa path foto asli
    save_requested   = QtCore.pyqtSignal(str)   # membawa username baru

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

    def update_wishlist_count(self, jumlah: int):
        """Update label total game di card Riwayat Wishlist."""
        for lbl in self.cardWishlist.findChildren(QtWidgets.QLabel):
            if lbl.text().startswith("Total:"):
                lbl.setText(f"Total: {jumlah} Game")
                break

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
        self.btnBack = QtWidgets.QPushButton("← Kembali")
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

        leftPanelLayout.addStretch()

        self.emptyLabel = QtWidgets.QLabel("Belum ada data preferensi game")
        self.emptyLabel.setObjectName("emptyLabel")
        self.emptyLabel.setAlignment(QtCore.Qt.AlignCenter)
        leftPanelLayout.addWidget(self.emptyLabel)

        leftPanelLayout.addStretch()

        # Logout
        self.btnLogout = QtWidgets.QPushButton("  Logout")
        self.btnLogout.setObjectName("btnLogout")
        self.btnLogout.setIcon(QtGui.QIcon(icon_path("material-symbols_logout-rounded.png")))
        self.btnLogout.setIconSize(QtCore.QSize(18, 18))
        self.btnLogout.clicked.connect(self.logout_clicked.emit)
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

        self.cardLike = make_card(
            "cardLike", "Vector.png", "Riwayat Like", "#FFFFFF",
            "Total: 0 Game", "Belum ada game yang di-like"
        )
        self.cardDislike = make_card(
            "cardDislike", "Vector (2).png", "Riwayat Dislike", "#FFFFFF",
            "Total: 0 Game", "Belum ada game yang di-dislike"
        )
        self.cardKomentar = make_card(
            "cardKomentar", "Vector (1).png", "Riwayat Komentar", "#FFFFFF",
            "Total: 0 Game", "Belum ada komentar"
        )

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


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ProfileWindow()
    window.show()
    sys.exit(app.exec_())