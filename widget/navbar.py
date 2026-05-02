# navbar.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor

from pages.dashboard.dashboard_logic import BORDER

BG_DARK = "#1e2840"
BG_ELEM = "#1e2840"
MUTED   = "#7b8db0"
WHITE   = "#ffffff"
GREEN   = "#00c853"


class Navbar(QWidget):
    search_changed    = pyqtSignal(str)
    dashboard_clicked = pyqtSignal()
    popular_clicked   = pyqtSignal()
    cheapest_clicked  = pyqtSignal()
    wishlist_clicked  = pyqtSignal()
    profile_clicked   = pyqtSignal()

    def __init__(self, active_page: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(
            f"background:{BG_DARK}; border-bottom:1px solid {BORDER};"
        )

        h = QHBoxLayout(self)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────────────────
        logo = QLabel("MAGER")
        logo.setStyleSheet(
            f"color:{WHITE}; font-size:20px; font-weight:900; "
            f"letter-spacing:1px; background:transparent;"
        )
        h.addWidget(logo)
        h.addSpacing(24)

        # ── Nav links ─────────────────────────────────────────────────────
        nav_links = [
            ("Dashboard",     self.dashboard_clicked),
            ("Popular Games", self.popular_clicked),
            ("Cheapest Games",self.cheapest_clicked),
        ]
        for name, signal in nav_links:
            is_active = (
                (name == "Dashboard"     and active_page == "dashboard") or
                (name == "Popular Games" and active_page == "popular")   or
                (name == "Cheapest Games"and active_page == "cheapest")
            )
            btn = QPushButton(name)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(
                f"QPushButton{{background:transparent; border:none;"
                f"color:{'#58a6ff' if is_active else MUTED};"
                f"font-size:13px; padding:8px 14px;"
                f"{'font-weight:bold;' if is_active else ''}}}"
                f"QPushButton:hover{{color:{WHITE};}}"
            )
            btn.clicked.connect(signal)
            h.addWidget(btn)

        h.addStretch()

        # ── Search ────────────────────────────────────────────────────────
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari game atau developer…")
        self.search.setFixedSize(200, 32)
        self.search.setStyleSheet(
            f"QLineEdit{{background:{BG_ELEM}; border:1px solid {BORDER};"
            f"border-radius:16px; padding:0 14px; color:{WHITE}; font-size:12px;}}"
            f"QLineEdit:focus{{border:1px solid {GREEN};}}"
        )
        self.search.textChanged.connect(self.search_changed)
        h.addWidget(self.search)
        h.addSpacing(10)

        # ── Wishlist button ───────────────────────────────────────────────
        wishlist_active = active_page == "wishlist"
        self.wishlist_btn = QPushButton("♥")
        self.wishlist_btn.setFixedSize(34, 34)
        self.wishlist_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.wishlist_btn.setToolTip("Wishlist")
        self.wishlist_btn.setStyleSheet(
            f"QPushButton{{background:{BG_ELEM};"
            f"border:1px solid {'#58a6ff' if wishlist_active else BORDER};"
            f"border-radius:17px;"
            f"color:{'#58a6ff' if wishlist_active else MUTED};"
            f"font-size:15px;}}"
            f"QPushButton:hover{{color:#f06292; border-color:#f06292;}}"
        )
        self.wishlist_btn.clicked.connect(self.wishlist_clicked)
        h.addWidget(self.wishlist_btn)
        h.addSpacing(8)

        # ── Profile button ────────────────────────────────────────────────
        profile_active = active_page == "profile"
        self.profile_btn = QPushButton("👤")
        self.profile_btn.setFixedSize(34, 34)
        self.profile_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.profile_btn.setToolTip("Profil Saya")
        self.profile_btn.setStyleSheet(
            f"QPushButton{{background:{BG_ELEM};"
            f"border:1px solid {'#58a6ff' if profile_active else BORDER};"
            f"border-radius:17px;"
            f"color:{'#58a6ff' if profile_active else MUTED};"
            f"font-size:14px;}}"
            f"QPushButton:hover{{color:{WHITE}; border-color:{WHITE};}}"
        )
        self.profile_btn.clicked.connect(self.profile_clicked)
        h.addWidget(self.profile_btn)