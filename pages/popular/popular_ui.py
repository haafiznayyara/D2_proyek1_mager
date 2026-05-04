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
    QSizePolicy, QGridLayout, QSpacerItem,
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QThread, QObject, QSize
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap, QLinearGradient,
    QBrush, QPen, QPalette, QCursor, QRadialGradient, QFontMetrics, QIcon
)
from widget.navbar import Navbar
from widget.cardGame import PopularGameCard, COVER_RATIO, INFO_H
from pages.popular.popular_logic import get_popular_games, sort_games, search_games

# ── Colour Palette (dark navy / green accent) ─────────────────────────────
BG        = "#0A1123"
BG2       = "#1A1F36"
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
        self.count_lbl = QLabel()
        self.count_lbl.setFont(QFont("Segoe UI", 9))
        self.count_lbl.setStyleSheet(f"color: {TEXT2}; padding-left: 4px;")
        outer.addWidget(self.count_lbl)

        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: transparent;")
        outer.addWidget(self.canvas)
        outer.addStretch()

        self._populate(games)

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
            lbl_t = QLabel("Peak Players")
            lbl_t.setFont(QFont("Segoe UI", 8))
            lbl_t.setStyleSheet(f"color: {TEXT2}; background: transparent; border : none;")
            fl.addWidget(lbl_t)
            fl.addStretch()
            lbl_n = QLabel(f"{g['peak_player']:,}")
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

# --- Popular Game Header --------------------------------------------------
class PopularHeader(QFrame):
    sort_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setFixedHeight(76)
        self.setObjectName("PopularHeader")

        self.setStyleSheet(f"""
            QFrame#PopularHeader {{
                background: {BORDER};
                border-radius: 10px;
                border: 1px solid {BORDER};
            }}
            QFrame#PopularHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        left = QVBoxLayout()
        left.setSpacing(2)
        left.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)

        icon = QLabel()
        pixmap = QPixmap("assets/green_arrow.png")
        icon.setPixmap(
            pixmap.scaled(
                22, 22,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        icon.setFixedSize(24, 24)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent; border: none;")
        title_row.addWidget(icon, alignment=Qt.AlignVCenter)

        title = QLabel("Game Populer")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT1}; background: transparent; border: none;")
        title_row.addWidget(title, alignment=Qt.AlignVCenter)

        title_row.addStretch()
        left.addLayout(title_row)

        subtitle = QLabel("Berdasarkan jumlah pemain tertinggi")
        subtitle.setFont(QFont("Segoe UI", 8))
        subtitle.setStyleSheet(f"color: {TEXT2}; background: transparent; border: none;")
        left.addWidget(subtitle)

        layout.addLayout(left)
        layout.addStretch()

        filter_icon = QIcon("assets/filter_outline.png")
        self.sort_btn = QPushButton("Tertinggi - Terendah")
        self.sort_btn.setIcon(filter_icon)
        self.sort_btn.setIconSize(QSize(16, 16))
        self.sort_btn.setFixedHeight(32)
        self.sort_btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.sort_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.sort_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SORT_BG};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {CARD_HOV};
                border-color: {ACCENT2};
            }}
        """)
        self.sort_btn.clicked.connect(self.sort_clicked.emit)
        layout.addWidget(self.sort_btn)


# ── Hero Banner ───────────────────────────────────────────────────────────
class HeroBanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(125)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 16)
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
        p.fillRect(self.rect(), QColor(BG))


# ── Main Window ───────────────────────────────────────────────────────────
class PopularGamesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAGER — Game Populer")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        # Load dari DB, default desc (peak tertinggi dulu)
        self._all_games  = get_popular_games(order="desc")
        self._sort_order = "desc"

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
        
        header_wrap = QWidget()
        header_wrap.setStyleSheet(f"background: {BG};")
        header_lay = QVBoxLayout(header_wrap)
        header_lay.setContentsMargins(20, 0, 20, 10)
        header_lay.setSpacing(0)

        self.popular_header = PopularHeader()
        header_lay.addWidget(self.popular_header)

        root.addWidget(header_wrap)

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

        self.grid = GamesGrid(self._all_games)
        self.grid.card_clicked.connect(self._on_card_clicked)

        # Sambungkan tombol sort di GamesGrid ke handler
        self.popular_header.sort_clicked.connect(self._toggle_sort)

        scroll.setWidget(self.grid)
        root.addWidget(scroll)

        self.nav.search_changed.connect(self._on_search)

    def _toggle_sort(self):
        self._sort_order = "asc" if self._sort_order == "desc" else "desc"
        label = "Terendah - Tertinggi" if self._sort_order == "asc" else "Tertinggi - Terendah"
        self.popular_header.sort_btn.setText(label)
        sorted_data = sort_games(self._all_games, self._sort_order)
        self.grid._populate(sorted_data)

    def _on_card_clicked(self, game: dict):
        print(f"[CLICKED] {game['title']} — peak: {game['peak_player']:,}")

    def _on_search(self, query: str):
        filtered = search_games(self._all_games, query)
        filtered = sort_games(filtered, self._sort_order)
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