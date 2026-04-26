from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QLineEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QRect, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap, QLinearGradient,
    QBrush, QPen, QPalette, QCursor, QRadialGradient
)

from dashboard_logic import (
    BG, CARD, CARD_HOV, ACCENT, ACCENT2, TEXT1, TEXT2, BORDER, TAG_BG,
    COLS, GAP, INFO_H, COVER_RATIO, CATEGORIES,
    fmt_price, rating_color, filter_games, ImageFetcher
)


def make_placeholder(game, w, h):
    px = QPixmap(w, h)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    g = QLinearGradient(0, 0, w, h)
    g.setColorAt(0, QColor("#161b22"))
    g.setColorAt(1, QColor("#0d1117"))
    p.fillRect(0, 0, w, h, g)

    rg = QRadialGradient(w * .5, h * .35, min(w, h) * .6)
    a = QColor(game["ac"]); a.setAlpha(70)
    b = QColor(game["ac"]); b.setAlpha(0)
    rg.setColorAt(0, a); rg.setColorAt(1, b)
    p.fillRect(0, 0, w, h, QBrush(rg))

    initials = "".join(word[0] for word in game["title"].split()[:3]).upper()
    font_size = max(18, min(36, w // 3))
    p.setPen(QColor(game["ac"]))
    p.setFont(QFont("Segoe UI", font_size, QFont.Bold))
    p.setOpacity(.55)
    p.drawText(QRect(0, 0, w, h), Qt.AlignCenter, initials)

    p.end()
    return px


# ── Rating Ring ───────────────────────────────────────────────────────────
class RatingRing(QWidget):
    def __init__(self, rating: int, parent=None):
        super().__init__(parent)
        self.rating = rating
        self.color  = QColor(rating_color(rating))
        self.setFixedSize(40, 40)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        m = 4
        rect = QRectF(m, m, self.width() - m * 2, self.height() - m * 2)

        bg_pen = QPen(QColor(BORDER))
        bg_pen.setWidth(3)
        p.setPen(bg_pen)
        p.drawEllipse(rect)

        prog_pen = QPen(self.color)
        prog_pen.setWidth(3)
        prog_pen.setCapStyle(Qt.RoundCap)
        p.setPen(prog_pen)
        start = 90 * 16
        span  = -int((self.rating / 100) * 360 * 16)
        p.drawArc(rect, start, span)

        p.setPen(QColor(TEXT1))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(rect.toRect(), Qt.AlignCenter, str(self.rating))


# ── GameCard ──────────────────────────────────────────────────────────────
class GameCard(QFrame):
    # Signal: dikirim ke GamesGrid saat card diklik
    clicked = pyqtSignal(dict)

    def __init__(self, game):
        super().__init__()
        self.game    = game
        self._cw     = 0
        self._raw_px = None

        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
            QFrame:hover {{ border-color: {ACCENT2}; }}
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.cover_lbl = QLabel()
        self.cover_lbl.setAlignment(Qt.AlignCenter)
        self.cover_lbl.setStyleSheet("border-radius: 12px 12px 0 0; background: transparent;")
        root.addWidget(self.cover_lbl)

        info = QWidget()
        info.setFixedHeight(INFO_H)
        il = QVBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 12)
        il.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.title_lbl = QLabel(game["title"])
        self.title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_lbl.setStyleSheet(f"color: {TEXT1};")
        self.title_lbl.setWordWrap(True)
        top_row.addWidget(self.title_lbl, stretch=1)

        self.ring = RatingRing(game["rating"])
        top_row.addWidget(self.ring, alignment=Qt.AlignTop)
        il.addLayout(top_row)

        genre_lbl = QLabel(game["genre"])
        genre_lbl.setFont(QFont("Segoe UI", 8))
        genre_lbl.setStyleSheet(f"""
            background: {TAG_BG}; color: {TEXT2};
            border-radius: 10px; border: 1px solid {BORDER};
            padding: 2px 10px;
        """)
        genre_lbl.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        il.addWidget(genre_lbl)
        il.addStretch()

        meta_lay = QVBoxLayout()
        meta_lay.setSpacing(1)
        dev_lbl = QLabel(game["dev"])
        dev_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        dev_lbl.setStyleSheet(f"color: {TEXT1};")
        pub_lbl = QLabel(f"oleh {game['pub']}")
        pub_lbl.setFont(QFont("Segoe UI", 7))
        pub_lbl.setStyleSheet(f"color: {TEXT2};")
        meta_lay.addWidget(dev_lbl)
        meta_lay.addWidget(pub_lbl)
        il.addLayout(meta_lay)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        il.addWidget(sep)

        price_lbl = QLabel(fmt_price(game["price"]))
        price_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        price_lbl.setStyleSheet(f"color: {ACCENT};")
        il.addWidget(price_lbl)

        root.addWidget(info)

        if game["img"]:
            self._fetch_image(game["img"])

    def mousePressEvent(self, event):
        """Emit signal saat card diklik."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)
        super().mousePressEvent(event)

    def _fetch_image(self, url):
        self._fetcher = ImageFetcher(url)
        self._fetcher.done.connect(self._on_image_data)
        self._fetcher.fetch_async()

    def _on_image_data(self, data):
        if data:
            px = QPixmap()
            px.loadFromData(data)
            if not px.isNull():
                self._raw_px = px
                self._apply_cover()

    def _apply_cover(self):
        if self._cw <= 0 or self._raw_px is None:
            return
        ch = int(self._cw * COVER_RATIO)
        scaled = self._raw_px.scaled(
            self._cw, ch,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        x = (scaled.width()  - self._cw) // 2
        y = (scaled.height() - ch)       // 2
        self.cover_lbl.setPixmap(scaled.copy(x, y, self._cw, ch))

    def set_width(self, w):
        if w == self._cw:
            return
        self._cw = w
        ch = int(w * COVER_RATIO)
        self.setFixedSize(w, ch + INFO_H)
        self.cover_lbl.setFixedSize(w, ch)

        if self._raw_px is not None:
            self._apply_cover()
        else:
            self.cover_lbl.setPixmap(make_placeholder(self.game, w, ch))

        fm = self.title_lbl.fontMetrics()
        self.title_lbl.setText(
            fm.elidedText(self.game["title"], Qt.ElideRight, w - 64)
        )


# ── GamesGrid ─────────────────────────────────────────────────────────────
class GamesGrid(QWidget):
    # Bubble-up signal dari card ke MainWindow
    card_clicked = pyqtSignal(dict)

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
            card = GameCard(g)
            card.setParent(self.canvas)
            card.show()
            # Teruskan sinyal klik ke atas
            card.clicked.connect(self.card_clicked)
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
            card.set_width(card_w)
            card.move(col * (card_w + GAP), row * (card_h + GAP))

        rows = (len(self.cards) + COLS - 1) // COLS
        self.canvas.setFixedHeight(rows * card_h + (rows - 1) * GAP + 4)

    def filter(self, cat, query=""):
        self._populate(filter_games(self._all_games, cat, query))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout()


# ── NavBar ────────────────────────────────────────────────────────────────
class NavBar(QWidget):
    search_changed   = pyqtSignal(str)
    wishlist_clicked = pyqtSignal()
    profile_clicked  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(54)
        self.setStyleSheet(f"background: {BG}; border-bottom: 1px solid {BORDER};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        logo = QLabel("MAGER")
        logo.setFont(QFont("Consolas", 16, QFont.Bold))
        logo.setStyleSheet(f"color: {TEXT1}; letter-spacing: 4px;")
        lay.addWidget(logo)
        lay.addSpacing(32)

        for name in ["Popular Games", "Cheapest Games"]:
            btn = QPushButton(name)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {TEXT2}; background: transparent;
                    border: none; font-size: 13px; padding: 0 14px;
                }}
                QPushButton:hover {{ color: {TEXT1}; }}
            """)
            lay.addWidget(btn)

        lay.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari game atau developer…")
        self.search.setFixedSize(220, 32)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {CARD}; border: 1px solid {BORDER};
                border-radius: 6px; color: {TEXT1};
                padding: 0 10px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT2}; }}
        """)
        self.search.textChanged.connect(self.search_changed)
        lay.addWidget(self.search)

        lay.addSpacing(8)

        _icon_style = f"""
            QPushButton {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                color: {TEXT2};
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {CARD_HOV};
                border-color: {ACCENT2};
                color: {TEXT1};
            }}
            QPushButton:pressed {{
                background: {ACCENT2};
                color: #000;
            }}
        """

        self.wishlist_btn = QPushButton("♡")
        self.wishlist_btn.setFixedSize(36, 36)
        self.wishlist_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.wishlist_btn.setToolTip("Wishlist")
        self.wishlist_btn.setStyleSheet(_icon_style)
        self.wishlist_btn.clicked.connect(self.wishlist_clicked)
        lay.addWidget(self.wishlist_btn)

        lay.addSpacing(6)

        self.profile_btn = QPushButton("⌂")
        self.profile_btn.setFixedSize(36, 36)
        self.profile_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.profile_btn.setToolTip("Profil Saya")
        self.profile_btn.setStyleSheet(_icon_style)
        self.profile_btn.clicked.connect(self.profile_clicked)
        lay.addWidget(self.profile_btn)


# ── CategoryBar ───────────────────────────────────────────────────────────
class CategoryBar(QWidget):
    category_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
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
        self.scroll.setFixedHeight(36)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        row = QHBoxLayout(inner)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self.cat_btns = {}
        self.active = "Semua"
        for cat in CATEGORIES:
            btn = QPushButton(cat)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _, c=cat: self._select(c))
            self.cat_btns[cat] = btn
            row.addWidget(btn)
        row.addStretch()

        self.scroll.setWidget(inner)
        outer.addWidget(self.scroll)

        self.right_btn = self._arrow("›")
        outer.addWidget(self.right_btn)

        self.left_btn.clicked.connect(lambda: self._scroll(-120))
        self.right_btn.clicked.connect(lambda: self._scroll(120))
        self._refresh()

    def _arrow(self, ch):
        b = QPushButton(ch)
        b.setFixedSize(28, 28)
        b.setCursor(QCursor(Qt.PointingHandCursor))
        b.setStyleSheet(f"""
            QPushButton {{
                background: {CARD}; border: 1px solid {BORDER};
                border-radius: 14px; color: {TEXT2}; font-size: 14px;
            }}
            QPushButton:hover {{ background: {CARD_HOV}; color: {TEXT1}; }}
        """)
        return b

    def _scroll(self, dx):
        sb = self.scroll.horizontalScrollBar()
        sb.setValue(sb.value() + dx)

    def _select(self, cat):
        self.active = cat
        self._refresh()
        self.category_changed.emit(cat)

    def _refresh(self):
        for cat, btn in self.cat_btns.items():
            if cat == self.active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {ACCENT}; color: #000;
                        border: none; border-radius: 14px;
                        font-size: 12px; font-weight: bold;
                        padding: 0 14px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {TAG_BG}; color: {TEXT2};
                        border: 1px solid {BORDER}; border-radius: 14px;
                        font-size: 12px; padding: 0 14px;
                    }}
                    QPushButton:hover {{
                        background: {CARD_HOV}; color: {TEXT1};
                        border-color: {ACCENT2};
                    }}
                """)


# ── MainWindow ────────────────────────────────────────────────────────────
class MainWindow(QWidget):
    # Signal diteruskan ke Router
    card_clicked     = pyqtSignal(dict)

    def __init__(self, games):
        super().__init__()

        self.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav = NavBar()
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
        s = QLabel("Cari game favoritmu dan beli dengan harga terjangkau.")
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