"""
MAGER - Halaman Wishlist
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QCursor
from widget.navbar import Navbar

# Palette (sync dengan dashboard)
BG      = "#0d1117"
BG_DARK = "#161b27"
BG_CARD = "#1a2035"
BG_ELEM = "#1e2840"
BORDER  = "#2a3555"
WHITE   = "#ffffff"
LIGHT   = "#c9d1e0"
MUTED   = "#7b8db0"
GREEN   = "#00c853"
RED     = "#e05252"
ACCENT  = "#58a6ff"

# Data wishlist dummy
WISHLIST_GAMES = [
    {
        "title": "Cyberpunk 2077",
        "genre": "RPG",
        "dev": "CD Projekt",
        "price": 299999,
        "old_price": 599999,
        "discount": 50,
        "rating": 86,
        "ac": "#ffd700",
    },
    {
        "title": "Elden Ring",
        "genre": "Action RPG",
        "dev": "FromSoftware",
        "price": 449000,
        "old_price": 449000,
        "discount": 0,
        "rating": 96,
        "ac": "#c0a060",
    },
    {
        "title": "Hades",
        "genre": "Roguelite",
        "dev": "Supergiant Games",
        "price": 89000,
        "old_price": 179000,
        "discount": 50,
        "rating": 94,
        "ac": "#e05252",
    },
    {
        "title": "Hollow Knight",
        "genre": "Metroidvania",
        "dev": "Team Cherry",
        "price": 59000,
        "old_price": 59000,
        "discount": 0,
        "rating": 95,
        "ac": "#7c6fa0",
    },
]


def fmt_price(p):
    if p == 0:
        return "Gratis"
    return f"Rp {p:,.0f}".replace(",", ".")


class WishlistCard(QFrame):
    remove_clicked = pyqtSignal(dict)
    view_clicked   = pyqtSignal(dict)

    def __init__(self, game: dict):
        super().__init__()
        self.game = game
        self.setObjectName("wcard")
        self.setStyleSheet(f"""
            QFrame#wcard {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QFrame#wcard:hover {{ border-color: {ACCENT}; }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(16)

        # Thumbnail warna
        thumb = QLabel()
        thumb.setFixedSize(72, 72)
        thumb.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {game['ac']}, stop:1 #0d1117);"
            f"border-radius:8px;"
        )
        initials = "".join(w[0] for w in game["title"].split()[:2]).upper()
        thumb.setText(initials)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setFont(QFont("Segoe UI", 16, QFont.Bold))
        thumb.setStyleSheet(
            thumb.styleSheet() +
            f"color: rgba(255,255,255,0.6);"
        )
        lay.addWidget(thumb)

        # Info tengah
        info = QVBoxLayout()
        info.setSpacing(4)

        title = QLabel(game["title"])
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color:{WHITE};background:transparent;")
        info.addWidget(title)

        meta = QHBoxLayout(); meta.setSpacing(8)
        genre = QLabel(game["genre"])
        genre.setStyleSheet(
            f"background:{BG_ELEM};color:{MUTED};font-size:10px;"
            "padding:2px 8px;border-radius:3px;"
        )
        dev = QLabel(game["dev"])
        dev.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        meta.addWidget(genre)
        meta.addWidget(dev)
        meta.addStretch()
        info.addLayout(meta)

        # Harga
        price_row = QHBoxLayout(); price_row.setSpacing(8)
        if game["discount"] > 0:
            badge = QLabel(f"-{game['discount']}%")
            badge.setStyleSheet(
                f"background:#1a7a3a;color:{GREEN};font-size:10px;"
                "font-weight:bold;padding:2px 7px;border-radius:3px;"
            )
            price_row.addWidget(badge)
            old = QLabel(fmt_price(game["old_price"]))
            old.setStyleSheet(
                f"color:{MUTED};font-size:11px;text-decoration:line-through;background:transparent;"
            )
            price_row.addWidget(old)
        price = QLabel(fmt_price(game["price"]))
        price.setFont(QFont("Segoe UI", 13, QFont.Bold))
        price.setStyleSheet(f"color:{GREEN};background:transparent;")
        price_row.addWidget(price)
        price_row.addStretch()
        info.addLayout(price_row)
        info.addStretch()

        lay.addLayout(info, stretch=1)

        # Tombol kanan
        btn_col = QVBoxLayout(); btn_col.setSpacing(6)

        btn_view = QPushButton("Lihat Detail")
        btn_view.setFixedHeight(34)
        btn_view.setCursor(QCursor(Qt.PointingHandCursor))
        btn_view.setStyleSheet(
            f"QPushButton{{background:{ACCENT};border:none;border-radius:6px;"
            f"color:#000;font-size:12px;font-weight:bold;padding:0 14px;}}"
            f"QPushButton:hover{{background:#79b8ff;}}"
        )
        btn_view.clicked.connect(lambda: self.view_clicked.emit(self.game))
        btn_col.addWidget(btn_view)

        btn_rm = QPushButton("✕ Hapus")
        btn_rm.setFixedHeight(34)
        btn_rm.setCursor(QCursor(Qt.PointingHandCursor))
        btn_rm.setStyleSheet(
            f"QPushButton{{background:transparent;border:1px solid {BORDER};"
            f"border-radius:6px;color:{MUTED};font-size:12px;padding:0 14px;}}"
            f"QPushButton:hover{{border-color:{RED};color:{RED};}}"
        )
        btn_rm.clicked.connect(lambda: self.remove_clicked.emit(self.game))
        btn_col.addWidget(btn_rm)

        lay.addLayout(btn_col)


class WishlistWindow(QWidget):
    back_clicked    = pyqtSignal()
    profile_clicked = pyqtSignal()
    card_clicked    = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._games = list(WISHLIST_GAMES)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav = Navbar(active_page="wishlist")
        self.nav.profile_clicked.connect(self.profile_clicked)
        root.addWidget(self.nav)

        # Header
        hdr = QWidget()
        hdr.setStyleSheet(f"background:{BG};")
        hl = QVBoxLayout(hdr)
        hl.setContentsMargins(28, 18, 28, 10)
        hl.setSpacing(4)

        top_row = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setCursor(QCursor(Qt.PointingHandCursor))
        btn_back.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;color:{MUTED};"
            f"font-size:13px;}} QPushButton:hover{{color:{WHITE};}}"
        )
        btn_back.clicked.connect(self.back_clicked)
        top_row.addWidget(btn_back)
        top_row.addStretch()
        hl.addLayout(top_row)

        t = QLabel("♡  Wishlist Saya")
        t.setFont(QFont("Segoe UI", 20, QFont.Bold))
        t.setStyleSheet(f"color:{WHITE};")
        hl.addWidget(t)

        self.sub_lbl = QLabel(f"{len(self._games)} game tersimpan")
        self.sub_lbl.setFont(QFont("Segoe UI", 10))
        self.sub_lbl.setStyleSheet(f"color:{MUTED};")
        hl.addWidget(self.sub_lbl)

        root.addWidget(hdr)

        # Scroll area berisi daftar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background:{BG}; border:none; }}
            QScrollBar:vertical {{ background:{BG_CARD}; width:6px; border-radius:3px; }}
            QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:20px; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
        """)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet(f"background:{BG};")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(28, 8, 28, 28)
        self.list_layout.setSpacing(10)

        self._populate()
        self.list_layout.addStretch()

        scroll.setWidget(self.list_widget)
        root.addWidget(scroll)

    def _populate(self):
        # Hapus semua card lama
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._games:
            empty = QLabel("Wishlist-mu masih kosong.\nTemukan game favoritmu di dashboard!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setFont(QFont("Segoe UI", 13))
            empty.setStyleSheet(f"color:{MUTED};padding:60px;")
            self.list_layout.addWidget(empty)
        else:
            for g in self._games:
                card = WishlistCard(g)
                card.remove_clicked.connect(self._remove_game)
                card.view_clicked.connect(self.card_clicked)
                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def _remove_game(self, game: dict):
        self._games = [g for g in self._games if g["title"] != game["title"]]
        self.sub_lbl.setText(f"{len(self._games)} game tersimpan")
        self._populate()