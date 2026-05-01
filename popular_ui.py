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


# ── Helpers ───────────────────────────────────────────────────────────────
def fmt_price(p: int) -> str:
    return f"Rp {p:,}".replace(",", ".")


def rating_color(r: int) -> str:
    if r >= 90:
        return ACCENT
    if r >= 75:
        return "#f1c40f"
    return "#e74c3c"


def make_placeholder(game: dict, w: int, h: int) -> QPixmap:
    px = QPixmap(w, h)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    g = QLinearGradient(0, 0, w, h)
    g.setColorAt(0, QColor("#0d1b2a"))
    g.setColorAt(1, QColor("#061020"))
    p.fillRect(0, 0, w, h, g)

    rg = QRadialGradient(w * .5, h * .4, min(w, h) * .65)
    a = QColor(game["ac"]); a.setAlpha(80)
    b = QColor(game["ac"]); b.setAlpha(0)
    rg.setColorAt(0, a); rg.setColorAt(1, b)
    p.fillRect(0, 0, w, h, QBrush(rg))

    initials = "".join(word[0] for word in game["title"].split()[:3]).upper()
    font_size = max(16, min(34, w // 3))
    p.setPen(QColor(game["ac"]))
    p.setFont(QFont("Segoe UI", font_size, QFont.Bold))
    p.setOpacity(0.5)
    p.drawText(QRectF(0, 0, w, h).toRect(), Qt.AlignCenter, initials)
    p.end()
    return px


# ── Rating Ring ───────────────────────────────────────────────────────────
class RatingRing(QWidget):
    def __init__(self, rating: int, parent=None):
        super().__init__(parent)
        self.rating = rating
        self.color  = QColor(rating_color(rating))
        self.setFixedSize(42, 42)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        m    = 4
        rect = QRectF(m, m, self.width() - m * 2, self.height() - m * 2)

        bg_pen = QPen(QColor(BORDER))
        bg_pen.setWidth(3)
        p.setPen(bg_pen)
        p.drawEllipse(rect)

        arc_pen = QPen(self.color)
        arc_pen.setWidth(3)
        arc_pen.setCapStyle(Qt.RoundCap)
        p.setPen(arc_pen)
        p.drawArc(rect, 90 * 16, -int(self.rating / 100 * 360 * 16))

        p.setPen(QColor(TEXT1))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(rect.toRect(), Qt.AlignCenter, str(self.rating))


# ── Tag Pill ──────────────────────────────────────────────────────────────
class TagPill(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 7))
        self.setStyleSheet(f"""
            background: {TAG_BG};
            color: {TEXT2};
            border: 1px solid {BORDER};
            border-radius: 9px;
            padding: 1px 8px;
        """)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ── Game Card ─────────────────────────────────────────────────────────────
class GameCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, game: dict, parent=None):
        super().__init__(parent)
        self.game    = game
        self._cw     = 0
        self._raw_px = None

        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
            QFrame:hover {{
                border-color: {ACCENT2};
                background: {CARD_HOV};
            }}
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Cover image area ──────────────────────────────────────────────
        self._cover_container = QWidget()
        self._cover_container.setStyleSheet("background: transparent;")
        cover_stack = QVBoxLayout(self._cover_container)
        cover_stack.setContentsMargins(0, 0, 0, 0)

        self.cover_lbl = QLabel()
        self.cover_lbl.setAlignment(Qt.AlignCenter)
        self.cover_lbl.setStyleSheet(
            "border-radius: 12px 12px 0 0; background: transparent;"
        )
        cover_stack.addWidget(self.cover_lbl)
        root.addWidget(self._cover_container)

        # ── Discount badge (absolute-ish via manual positioning) ──────────
        self._badge = QLabel(f"-{game['discount']}%")
        self._badge.setParent(self)
        self._badge.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self._badge.setStyleSheet(f"""
            background: {DISCOUNT};
            color: #000;
            border-radius: 5px;
            padding: 2px 7px;
        """)
        self._badge.adjustSize()

        # ── Wishlist heart button ─────────────────────────────────────────
        self._wish_btn = QPushButton("♡")
        self._wish_btn.setParent(self)
        self._wish_btn.setFixedSize(28, 28)
        self._wish_btn.setFont(QFont("Segoe UI", 12))
        self._wish_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._wish_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(13,27,42,0.75);
                border: 1px solid {BORDER};
                border-radius: 14px;
                color: {TEXT2};
            }}
            QPushButton:hover {{ color: #e74c3c; border-color: #e74c3c; }}
        """)

        # ── Info panel ────────────────────────────────────────────────────
        info = QWidget()
        info.setFixedHeight(INFO_H)
        info.setStyleSheet("background: transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 10)
        il.setSpacing(5)

        # Title + rating ring
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        self.title_lbl = QLabel(game["title"])
        self.title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_lbl.setStyleSheet(f"color: {TEXT1};border: none;")
        self.title_lbl.setWordWrap(False)
        title_row.addWidget(self.title_lbl, stretch=1)
        self.ring = RatingRing(game["rating"])
        title_row.addWidget(self.ring, alignment=Qt.AlignTop | Qt.AlignRight)
        il.addLayout(title_row)

        # Tag pills row
        tags_row = QHBoxLayout()
        tags_row.setSpacing(4)
        tags_row.setContentsMargins(0, 0, 0, 0)
        for tag in game["tags"][:3]:
            tags_row.addWidget(TagPill(tag))
        tags_row.addStretch()
        il.addLayout(tags_row)

        # Developer / publisher
        dev_lbl = QLabel(game["dev"])
        dev_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        dev_lbl.setStyleSheet(f"color: {TEXT1};border: none;")
        il.addWidget(dev_lbl)

        pub_lbl = QLabel(game["pub"])
        pub_lbl.setFont(QFont("Segoe UI", 7))
        pub_lbl.setStyleSheet(f"color: {TEXT2};border: none;")
        il.addWidget(pub_lbl)

        il.addStretch()

        # Prices
        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        orig_lbl = QLabel(fmt_price(game["orig"]))
        orig_lbl.setFont(QFont("Segoe UI", 8))
        orig_lbl.setStyleSheet(f"color: {PRICE_OLD}; text-decoration: line-through;border: none;")
        price_row.addWidget(orig_lbl)
        disc_lbl = QLabel(fmt_price(game["price"]))
        disc_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        disc_lbl.setStyleSheet(f"color: {ACCENT}; border: none;")
        price_row.addWidget(disc_lbl)
        price_row.addStretch()
        il.addLayout(price_row)

        root.addWidget(info)

    # ── Interactions ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)
        super().mousePressEvent(event)

    # ── Sizing ────────────────────────────────────────────────────────────
    def set_width(self, w: int):
        if w == self._cw:
            return
        self._cw = w
        ch = int(w * COVER_RATIO)
        self.setFixedSize(w, ch + INFO_H)
        self.cover_lbl.setFixedSize(w, ch)
        self._cover_container.setFixedSize(w, ch)

        if self._raw_px is not None:
            self._apply_cover()
        else:
            self.cover_lbl.setPixmap(make_placeholder(self.game, w, ch))

        # Position floating badge & wishlist
        self._badge.move(8, 8)
        self._badge.raise_()
        self._wish_btn.move(w - 36, 6)
        self._wish_btn.raise_()

        # Elide title
        fm = QFontMetrics(self.title_lbl.font())
        self.title_lbl.setText(
            fm.elidedText(self.game["title"], Qt.ElideRight, w - 68)
        )

    def _apply_cover(self):
        if self._cw <= 0 or self._raw_px is None:
            return
        ch = int(self._cw * COVER_RATIO)
        scaled = self._raw_px.scaled(
            self._cw, ch,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        x = (scaled.width()  - self._cw) // 2
        y = (scaled.height() - ch)       // 2
        self.cover_lbl.setPixmap(scaled.copy(x, y, self._cw, ch))


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
            card = GameCard(g)
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


# ── NavBar ────────────────────────────────────────────────────────────────
class NavBar(QWidget):
    search_changed   = pyqtSignal(str)
    wishlist_clicked = pyqtSignal()
    profile_clicked  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(56)
        self.setStyleSheet(
            f"background: {BG}; border-bottom: 1px solid {BORDER};"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(0)

        # Logo
        logo = QLabel("MAGER")
        logo.setFont(QFont("Consolas", 16, QFont.Bold))
        logo.setStyleSheet(f"color: {TEXT1}; letter-spacing: 4px;")
        lay.addWidget(logo)
        lay.addSpacing(36)

        # Nav links
        self._nav_btns = {}
        for name, active in [("Game Populer", True), ("Filter Harga", False)]:
            btn = QPushButton(name)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            style_active   = f"color: {ACCENT}; background: transparent; border: none; font-size: 13px; font-weight: bold; padding: 0 14px;"
            style_inactive = f"color: {TEXT2}; background: transparent; border: none; font-size: 13px; padding: 0 14px;"
            btn.setStyleSheet(style_active if active else style_inactive)
            btn.clicked.connect(lambda _, n=name: self._set_active(n))
            self._nav_btns[name] = btn
            lay.addWidget(btn)

        lay.addStretch()

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search games…")
        self.search.setFixedSize(220, 32)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 6px;
                color: {TEXT1};
                padding: 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT2}; }}
        """)
        self.search.textChanged.connect(self.search_changed)
        lay.addWidget(self.search)
        lay.addSpacing(10)

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
        """

        wish = QPushButton("♡")
        wish.setFixedSize(36, 36)
        wish.setCursor(QCursor(Qt.PointingHandCursor))
        wish.setToolTip("Wishlist")
        wish.setStyleSheet(_icon_style)
        wish.clicked.connect(self.wishlist_clicked)
        lay.addWidget(wish)
        lay.addSpacing(8)

        prof = QPushButton("👤")
        prof.setFixedSize(36, 36)
        prof.setCursor(QCursor(Qt.PointingHandCursor))
        prof.setToolTip("Profil")
        prof.setStyleSheet(_icon_style)
        prof.clicked.connect(self.profile_clicked)
        lay.addWidget(prof)

    def _set_active(self, name: str):
        for n, btn in self._nav_btns.items():
            if n == name:
                btn.setStyleSheet(
                    f"color: {ACCENT}; background: transparent; border: none; "
                    f"font-size: 13px; font-weight: bold; padding: 0 14px;"
                )
            else:
                btn.setStyleSheet(
                    f"color: {TEXT2}; background: transparent; border: none; "
                    f"font-size: 13px; padding: 0 14px;"
                )


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

        self.nav = NavBar()
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