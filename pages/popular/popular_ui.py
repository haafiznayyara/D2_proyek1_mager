"""
popular_games_ui.py
───────────────────
PyQt5 UI for the "Game Populer" dashboard page.
Design reference: Popular_Games__Lowest_.png
Code style reference: dashboard_ui.py

Run standalone:
    python popular_games_ui.py
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QLineEdit,
    QSizePolicy, QGridLayout, QSpacerItem
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QThread, QObject, QSize
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap, QLinearGradient,
    QBrush, QPen, QPalette, QCursor, QRadialGradient, QFontMetrics
)
from widget.navbar import Navbar
from widget.cardGame import PopularGameCard, COVER_RATIO, INFO_H

# ── Colour Palette (dark navy / green accent) ─────────────────────────────
BG        = "#0A1123"
BG2       = "#0f2236"
CARD      = "#1A2332"
CARD_HOV  = "#1A2332"
ACCENT    = "#39d353"       # green
ACCENT2   = "#2ea84a"
TEXT1     = "#e8eaf0"
TEXT2     = "#8899aa"
BORDER    = "#1e3a50"
TAG_BG    = "#162840"
DISCOUNT  = "#39d353"
PRICE_OLD = "#556677"
SORT_BG   = "#1a3350"

# ── Layout constants ──────────────────────────────────────────────────────
COLS        = 5
GAP         = 14
COVER_RATIO = 0.58   # cover_h / card_w
INFO_H      = 183    # fixed info panel height per card (no footer)
FOOTER_H    = 28     # height of the separate "Tertinggi" bar below card
FOOTER_GAP  = 5      # gap between card bottom and footer bar

# ── Game data ─────────────────────────────────────────────────────────────
GAMES = [
    {
        "title":    "God of War Ragnarök",
        "tags":     ["Action", "Adventure", "Story Rich"],
        "dev":      "Santa Monica Studio",
        "pub":      "Sony Interactive Entertainment",
        "rating":   94,
        "price":    599_999,
        "orig":     799_999,
        "discount": 25,
        "players":  35_615,
        "ac":       "#c0392b",
        "img":      None,
    },
    {
        "title":    "Hades",
        "tags":     ["Action", "Indie", "RPG"],
        "dev":      "Supergiant Games",
        "pub":      "Supergiant Games",
        "rating":   93,
        "price":    149_999,
        "orig":     249_999,
        "discount": 40,
        "players":  54_240,
        "ac":       "#e67e22",
        "img":      None,
    },
    {
        "title":    "Hollow Knight",
        "tags":     ["Platform", "Indie", "Adventure"],
        "dev":      "Team Cherry",
        "pub":      "Team Cherry",
        "rating":   95,
        "price":    89_999,
        "orig":     149_999,
        "discount": 40,
        "players":  95_655,
        "ac":       "#2980b9",
        "img":      None,
    },
    {
        "title":    "Red Dead Redemption 2",
        "tags":     ["Action", "Adventure", "Open World"],
        "dev":      "Rockstar Games",
        "pub":      "Rockstar Games",
        "rating":   91,
        "price":    399_999,
        "orig":     799_999,
        "discount": 50,
        "players":  99_993,
        "ac":       "#c0392b",
        "img":      None,
    },
    {
        "title":    "The Witcher 3",
        "tags":     ["RPG", "Open World", "Story Rich"],
        "dev":      "CD Projekt Red",
        "pub":      "CD Projekt",
        "rating":   92,
        "price":    179_999,
        "orig":     449_999,
        "discount": 60,
        "players":  102_417,
        "ac":       "#8e44ad",
        "img":      None,
    },
    {
        "title":    "Resident Evil 4 Remake",
        "tags":     ["Horror", "Action", "Shooter"],
        "dev":      "Capcom",
        "pub":      "Capcom",
        "rating":   90,
        "price":    359_999,
        "orig":     599_999,
        "discount": 40,
        "players":  48_220,
        "ac":       "#16a085",
        "img":      None,
    },
    {
        "title":    "Stardew Valley",
        "tags":     ["Simulation", "Indie", "Casual"],
        "dev":      "ConcernedApe",
        "pub":      "ConcernedApe",
        "rating":   98,
        "price":    67_999,
        "orig":     99_999,
        "discount": 33,
        "players":  142_880,
        "ac":       "#27ae60",
        "img":      None,
    },
    {
        "title":    "Baldur's Gate 3",
        "tags":     ["RPG", "Strategy", "Story Rich"],
        "dev":      "Larian Studios",
        "pub":      "Larian Studios",
        "rating":   97,
        "price":    599_999,
        "orig":     799_999,
        "discount": 25,
        "players":  88_540,
        "ac":       "#8e44ad",
        "img":      None,
    },
    {
        "title":    "Elden Ring",
        "tags":     ["Action", "RPG", "Open World"],
        "dev":      "FromSoftware",
        "pub":      "Bandai Namco",
        "rating":   96,
        "price":    399_999,
        "orig":     799_999,
        "discount": 50,
        "players":  121_660,
        "ac":       "#d4ac0d",
        "img":      None,
    },
    {
        "title":    "Cyberpunk 2077",
        "tags":     ["Action", "RPG", "Open World"],
        "dev":      "CD Projekt Red",
        "pub":      "CD Projekt",
        "rating":   87,
        "price":    249_999,
        "orig":     499_999,
        "discount": 50,
        "players":  77_330,
        "ac":       "#f39c12",
        "img":      None,
    },
]

# ── Games Grid ────────────────────────────────────────────────────────────
class GamesGrid(QWidget):
    card_clicked = pyqtSignal(dict)

    def __init__(self, games: list):
        super().__init__()
        self._all_games = games
        self.cards      = []
        self.setStyleSheet(f"background: {BG};")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 0, 20, 20)
        outer.setSpacing(8)

        # Section header
        hdr = QWidget()
        hdr.setStyleSheet(f"""
            background: {BG2};
            border-radius: 10px;
            border: 1px solid {BORDER};
            QLabel {{ border: none; }}
        """)
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 12, 14, 12)

        hdr_left = QVBoxLayout()
        hdr_left.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)
        arrow_lbl = QLabel("↑")
        arrow_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        arrow_lbl.setStyleSheet(f"color: {ACCENT}; border: none;")
        arrow_lbl.setFixedSize(22, 22)
        title_row.addWidget(arrow_lbl, alignment=Qt.AlignVCenter)
        sec_title = QLabel("Game Populer")
        sec_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sec_title.setStyleSheet(f"color: {TEXT1}; border: none;")
        title_row.addWidget(sec_title, alignment=Qt.AlignVCenter)
        title_row.addStretch()
        hdr_left.addLayout(title_row)

        sec_sub = QLabel("        Berdasarkan jumlah pemain tertinggi")
        sec_sub.setFont(QFont("Segoe UI", 8))
        sec_sub.setStyleSheet(f"color: {TEXT2}; border: none;")
        hdr_left.addWidget(sec_sub)

        hdr_lay.addLayout(hdr_left)
        hdr_lay.addStretch()

        self.sort_btn = QPushButton("⇅  Terendah - Tertinggi")
        self.sort_btn.setFixedHeight(36)
        self.sort_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.sort_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.sort_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SORT_BG};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: {CARD_HOV};
                border-color: {ACCENT2};
            }}
        """)
        hdr_lay.addWidget(self.sort_btn)
        outer.addWidget(hdr)

        self.count_lbl = QLabel()
        self.count_lbl.setFont(QFont("Segoe UI", 9))
        self.count_lbl.setStyleSheet(f"color: {TEXT2}; padding-left: 4px;")
        outer.addWidget(self.count_lbl)

        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: transparent;")
        outer.addWidget(self.canvas)
        outer.addStretch()

        self._sorted_asc = True
        self.sort_btn.clicked.connect(self._toggle_sort)
        self._populate(games)

    def _toggle_sort(self):
        self._sorted_asc = not self._sorted_asc
        label = "Terendah - Tertinggi" if self._sorted_asc else "Tertinggi - Terendah"
        self.sort_btn.setText(f"⇅  {label}")
        sorted_games = sorted(
            self._all_games,
            key=lambda g: g["players"],
            reverse=not self._sorted_asc,
        )
        self._populate(sorted_games)

    def _populate(self, games: list):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        for f in getattr(self, '_footers', []):
            f.setParent(None)
            f.deleteLater()
        self.cards   = []
        self._footers = []
        self.count_lbl.setText(f"Menampilkan {len(games)} game")
        for g in games:
            card = PopularGameCard(g)
            card.setParent(self.canvas)
            card.show()
            card.clicked.connect(self.card_clicked)
            self.cards.append(card)

            # ── Separate "Tertinggi" footer bar ───────────────────────────
            footer = QWidget(self.canvas)
            footer.setFixedHeight(FOOTER_H)
            footer.setStyleSheet(f"""
                background: {CARD};
                border-radius: 0 0 14px 14px;
                border: 1px solid {BORDER};
                border-top: none;
            """)
            fl = QHBoxLayout(footer)
            fl.setContentsMargins(12, 0, 12, 0)
            fl.setSpacing(0)
            lbl_t = QLabel("Tertinggi")
            lbl_t.setFont(QFont("Segoe UI", 8))
            lbl_t.setStyleSheet(f"color: {TEXT2}; background: transparent; border : none;")
            fl.addWidget(lbl_t)
            fl.addStretch()
            lbl_n = QLabel(f"{g['players']:,}")
            lbl_n.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lbl_n.setStyleSheet(f"color: {ACCENT}; background: transparent; border : none;")
            fl.addWidget(lbl_n)
            footer.show()
            self._footers.append(footer)

        self._relayout()

    def _relayout(self):
        if not self.cards:
            self.canvas.setFixedHeight(10)
            return
        avail = self.canvas.width()
        if avail < 50:
            avail = self.width() - 40
        if avail < 50:
            return

        card_w  = max(120, (avail - GAP * (COLS - 1)) // COLS)
        cover_h = int(card_w * COVER_RATIO)
        card_h  = cover_h + INFO_H
        # total slot height = card + gap + footer
        slot_h  = card_h + FOOTER_GAP + FOOTER_H

        for i, (card, footer) in enumerate(zip(self.cards, self._footers)):
            row, col = divmod(i, COLS)
            x = col * (card_w + GAP)
            y = row * (slot_h + GAP)
            card.set_width(card_w)
            card.move(x, y)
            footer.setFixedWidth(card_w)
            footer.move(x, y + card_h + FOOTER_GAP)

        rows = (len(self.cards) + COLS - 1) // COLS
        total_h = rows * slot_h + (rows - 1) * GAP + 4
        self.canvas.setFixedHeight(total_h)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout()


# ── Hero Banner ───────────────────────────────────────────────────────────
class HeroBanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(90)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 10)
        lay.setSpacing(4)

        title = QLabel("Temukan Game Terbaik dengan Harga Terbaik")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT1};")
        lay.addWidget(title)

        sub = QLabel("Cari game dengan harga terbaik di waktu yang tepat")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {TEXT2};")
        lay.addWidget(sub)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0.0, QColor("#0d1b2a"))
        g.setColorAt(1.0, QColor("#061020"))
        p.fillRect(self.rect(), g)


# ── Main Window ───────────────────────────────────────────────────────────
class PopularGamesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAGER — Game Populer")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav = Navbar(active_page="popular")
        root.addWidget(self.nav)

        self.hero = HeroBanner()
        root.addWidget(self.hero)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {BG}; border: none; }}
            QScrollBar:vertical {{
                background: {CARD}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT2}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self.grid = GamesGrid(GAMES)
        self.grid.card_clicked.connect(self._on_card_clicked)
        scroll.setWidget(self.grid)
        root.addWidget(scroll)

        self.nav.search_changed.connect(self._on_search)

    def _on_card_clicked(self, game: dict):
        print(f"[CLICKED] {game['title']} — {fmt_price(game['price'])}")

    def _on_search(self, query: str):
        q = query.strip().lower()
        filtered = [
            g for g in GAMES
            if q in g["title"].lower()
            or q in g["dev"].lower()
            or any(q in t.lower() for t in g["tags"])
        ]
        self.grid._populate(filtered)


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window,     QColor(BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT1))
    palette.setColor(QPalette.Base,       QColor(CARD))
    palette.setColor(QPalette.Text,       QColor(TEXT1))
    palette.setColor(QPalette.Button,     QColor(CARD))
    palette.setColor(QPalette.ButtonText, QColor(TEXT1))
    app.setPalette(palette)

    win = PopularGamesWindow()
    win.show()
    sys.exit(app.exec_())