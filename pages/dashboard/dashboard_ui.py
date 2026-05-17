from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QLineEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QRect, QRectF, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap, QLinearGradient,
    QBrush, QPen, QPalette, QCursor, QRadialGradient
)

from pages.dashboard.dashboard_logic import (
    BG, CARD, CARD_HOV, ACCENT, ACCENT2, TEXT1, TEXT2, BORDER, TAG_BG,
    COLS, GAP, INFO_H, COVER_RATIO,
    fmt_price, rating_color, filter_games, ImageFetcher, get_categories_from_db
)
from widget.navbar import Navbar
from widget.cardGame import PopularGameCard, COVER_RATIO as _COVER_RATIO, INFO_H as _INFO_H


# ── GamesGrid ─────────────────────────────────────────────────────────────
class GamesGrid(QWidget):
    # Bubble-up signal dari card ke MainWindow
    card_clicked = pyqtSignal(dict)
    wishlist_clicked = pyqtSignal(dict) 

    def __init__(self, games):
        super().__init__()
        self._all_games = games
        self.cards = []
        self.setStyleSheet(f"background: {BG};")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 8, 16, 16)
        outer.setSpacing(6)

        self.count_lbl = QLabel()
        self.count_lbl.setFont(QFont("Segoe UI", 9))
        self.count_lbl.setStyleSheet(f"color: {TEXT2};")
        outer.addWidget(self.count_lbl)

        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: transparent;")
        outer.addWidget(self.canvas)
        outer.addStretch()

        self._populate(games)

    def _populate(self, games):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []
        self.count_lbl.setText(f"Menampilkan {len(games)} game")
        for g in games:
            card = PopularGameCard(g)
            card.setParent(self.canvas)
            card.show()
            # Teruskan sinyal klik ke atas
            card.clicked.connect(self.card_clicked)
            card.wishlist_clicked.connect(self.wishlist_clicked)          
            self.cards.append(card)
        self._relayout()

    def _relayout(self):
        if not self.cards:
            self.canvas.setFixedHeight(10)
            return

        avail = self.canvas.width()
        if avail < 50:
            avail = self.width() - 32
        if avail < 50:
            return

        card_w  = max(120, (avail - GAP * (COLS - 1)) // COLS)
        cover_h = int(card_w * COVER_RATIO)
        card_h  = cover_h + INFO_H

        for i, card in enumerate(self.cards):
            row, col = divmod(i, COLS)
            x = col * (card_w + GAP)
            y = row * (card_h + GAP)   # ← tambahkan GAP vertikal di sini
            card.set_width(card_w)
            card.move(x, y)

        rows = (len(self.cards) + COLS - 1) // COLS
        total_h = rows * card_h + (rows - 1) * GAP + 4   # ← hitung total dengan GAP
        self.canvas.setFixedHeight(total_h)

    def filter(self, cat, query=""):
        self._populate(filter_games(self._all_games, cat, query))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout()

# ── CategoryBar ───────────────────────────────────────────────────────────
class CategoryBar(QWidget):
    category_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(62)
        self.setStyleSheet(f"background: {BG};")
        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 8, 20, 8)
        outer.setSpacing(6)

        self.left_btn = self._arrow("‹")
        outer.addWidget(self.left_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setFixedHeight(48)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        row = QHBoxLayout(inner)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self.cat_btns = {}
        self.active = "Semua"
        for cat in get_categories_from_db():
            btn = QPushButton(cat)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, c=cat: self._select(c))
            self.cat_btns[cat] = btn
            row.addWidget(btn)
        row.addStretch()

        self.scroll.setWidget(inner)
        outer.addWidget(self.scroll)

        self.right_btn = self._arrow("›")
        outer.addWidget(self.right_btn)

        self.left_btn.clicked.connect(lambda: self._scroll(-500))
        self.right_btn.clicked.connect(lambda: self._scroll(500))
        self._refresh()

    def _arrow(self, ch):
        b = QPushButton(ch)
        b.setFixedSize(36, 36)
        b.setCursor(QCursor(Qt.PointingHandCursor))
        b.setStyleSheet(f"""
            QPushButton {{
                background: {TAG_BG}; border: 1px solid {BORDER};
                border-radius: 10px; color: {TEXT1}; font-size: 20px;
            }}
            QPushButton:hover {{ background: {CARD_HOV}; color: {TEXT1}; border-color: {ACCENT} }}
        """)
        return b

    def _scroll(self, dx):
        sb = self.scroll.horizontalScrollBar()
        self._anim = QPropertyAnimation(sb, b"value")
        self._anim.setDuration(300)
        self._anim.setStartValue(sb.value())
        self._anim.setEndValue(sb.value() + dx)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def _select(self, cat):
        self.active = cat
        self._refresh()
        self.category_changed.emit(cat)

    def _refresh(self):
        for cat, btn in self.cat_btns.items():
            if cat == self.active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {ACCENT}; color: #000000;
                        border: none; border-radius: 10px;
                        font-size: 13px; font-weight: bold;
                        padding: 0 20px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {TAG_BG}; color: {TEXT1};
                        border: 1px solid {BORDER}; border-radius: 10px;
                        font-size: 13px; 
                        padding: 0 20px;
                    }}
                    QPushButton:hover {{
                        background: {ACCENT}; color: #000000;
                        border-color: {ACCENT};
                    }}
                    QPushButton:checked {{
                        background: {ACCENT}; color: #000000;
                        border-color: {ACCENT};
                    }}
                """)


# ── MainWindow ────────────────────────────────────────────────────────────
class MainWindow(QWidget):
    # Signal diteruskan ke Router
    card_clicked     = pyqtSignal(dict)
    wishlist_clicked = pyqtSignal(dict)

    def __init__(self, games):
        super().__init__()

        self.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav = Navbar(active_page="dashboard")
        self.nav.setAttribute(Qt.WA_StyledBackground, True)
        self.nav.setStyleSheet("background: #000000;")
        root.addWidget(self.nav)

        header = QWidget()
        header.setStyleSheet(f"background: {BG};")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 8)
        hl.setSpacing(3)
        t = QLabel("Temukan Game Terbaik dengan Harga Terbaik")
        t.setFont(QFont("Segoe UI", 20, QFont.Bold))
        t.setStyleSheet(f"color: {TEXT1};")
        hl.addWidget(t)
        s = QLabel("Cari game favoritmu dan beli dengan harga terjangkau")
        s.setFont(QFont("Segoe UI", 11))
        s.setStyleSheet(f"color: {TEXT2};")
        hl.addWidget(s)
        root.addWidget(header)

        self.cat_bar = CategoryBar()
        root.addWidget(self.cat_bar)

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

        self.grid_widget = GamesGrid(games)
        # Bubble-up card click ke MainWindow → Router
        self.grid_widget.card_clicked.connect(self.card_clicked)
        self.grid_widget.wishlist_clicked.connect(self.wishlist_clicked)
        scroll.setWidget(self.grid_widget)
        root.addWidget(scroll)

        self._active_cat   = "Semua"
        self._active_query = ""

        self.cat_bar.category_changed.connect(self._on_cat_changed)
        self.nav.search_changed.connect(self._on_search_changed)

    def _on_cat_changed(self, cat: str):
        self._active_cat = cat
        self.grid_widget.filter(self._active_cat, self._active_query)

    def _on_search_changed(self, query: str):
        self._active_query = query
        self.grid_widget.filter(self._active_cat, self._active_query)