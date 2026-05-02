# widget/popular_card.py
from fileinput import filename
from fileinput import filename
from importlib.resources import path
from importlib.resources import path
import os
from PyQt5.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap, QLinearGradient,
    QBrush, QPen, QCursor, QRadialGradient, QFontMetrics
)

# ── Palette ───────────────────────────────────────────────────────────────
CARD      = "#1A2332"
CARD_HOV  = "#1A2332"
ACCENT    = "#39d353"
ACCENT2   = "#2ea84a"
TEXT1     = "#e8eaf0"
TEXT2     = "#8899aa"
BORDER    = "#1e3a50"
TAG_BG    = "#162840"

COVER_RATIO = 0.58
INFO_H      = 183

# Path absolut agar tidak bergantung pada working directory
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTER_DIR = os.path.join(BASE_DIR, "assets", "posters")


# ── Helpers ───────────────────────────────────────────────────────────────
def fmt_price(p: int) -> str:
    if p == 0:
        return "Gratis"
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
    a = QColor(game.get("ac", "#39d353")); a.setAlpha(80)
    b = QColor(game.get("ac", "#39d353")); b.setAlpha(0)
    rg.setColorAt(0, a); rg.setColorAt(1, b)
    p.fillRect(0, 0, w, h, QBrush(rg))

    initials = "".join(word[0] for word in game["title"].split()[:3]).upper()
    font_size = max(16, min(34, w // 3))
    p.setPen(QColor(game.get("ac", "#39d353")))
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


# ── Game Card (shared, reusable) ──────────────────────────────────────────
class PopularGameCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, game: dict, parent=None):
        super().__init__(parent)
        self.game    = game
        self._cw     = 0
        self._poster = None  # QPixmap mentah, di-crop saat set_width

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

        # ── Cover ─────────────────────────────────────────────────────────
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

        # ── Wishlist button (floating) ────────────────────────────────────
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
        self.title_lbl.setStyleSheet(f"color: {TEXT1}; border: none;")
        self.title_lbl.setWordWrap(False)
        title_row.addWidget(self.title_lbl, stretch=1)
        self.ring = RatingRing(game["rating"])
        title_row.addWidget(self.ring, alignment=Qt.AlignTop | Qt.AlignRight)
        il.addLayout(title_row)

        # Tags — pakai "tags" (popular) atau fallback ke "genre" (dashboard)
        tags_row = QHBoxLayout()
        tags_row.setSpacing(4)
        tags_row.setContentsMargins(0, 0, 0, 0)
        tags = game.get("tags") or ([game["genre"]] if game.get("genre") else [])
        for tag in tags[:3]:
            tags_row.addWidget(TagPill(tag))
        tags_row.addStretch()
        il.addLayout(tags_row)

        # Developer / publisher
        dev_lbl = QLabel(game["dev"])
        dev_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        dev_lbl.setStyleSheet(f"color: {TEXT1}; border: none;")
        il.addWidget(dev_lbl)

        pub_lbl = QLabel(f"oleh {game['pub']}")
        pub_lbl.setFont(QFont("Segoe UI", 7))
        pub_lbl.setStyleSheet(f"color: {TEXT2}; border: none;")
        il.addWidget(pub_lbl)

        il.addStretch()

        # Harga
        price_lbl = QLabel(fmt_price(game["price"]))
        price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        price_lbl.setStyleSheet(f"color: {ACCENT}; border: none;")
        il.addWidget(price_lbl)

        root.addWidget(info)

        # Load poster sekali di __init__, crop dilakukan di set_width
        self._poster = self._load_poster_raw()

    def _load_poster_raw(self) -> QPixmap | None:
        filename = self.game.get("img", "")
        
        # Handle jika nilai adalah None, string "None", atau string kosong
        if not filename or str(filename).strip().lower() in ("none", "null", ""):
            return None
        
        path = os.path.join(POSTER_DIR, str(filename).strip())
        if not os.path.exists(path):
            print(f"[DEBUG] file tidak ditemukan: {path}")
            return None
        
        px = QPixmap(path)
        return None if px.isNull() else px

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)
        super().mousePressEvent(event)

    def set_width(self, w: int):
        if w == self._cw:
            return
        self._cw = w
        ch = int(w * COVER_RATIO)
        self.setFixedSize(w, ch + INFO_H)
        self.cover_lbl.setFixedSize(w, ch)
        self._cover_container.setFixedSize(w, ch)

        # Crop poster ke ukuran card saat ini, fallback ke placeholder
        if self._poster and not self._poster.isNull():
            scaled = self._poster.scaled(
                w, ch,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (scaled.width()  - w) // 2
            y = (scaled.height() - ch) // 2
            self.cover_lbl.setPixmap(scaled.copy(x, y, w, ch))
        else:
            self.cover_lbl.setPixmap(make_placeholder(self.game, w, ch))

        self._wish_btn.move(w - 36, 6)
        self._wish_btn.raise_()

        fm = QFontMetrics(self.title_lbl.font())
        self.title_lbl.setText(
            fm.elidedText(self.game["title"], Qt.ElideRight, w - 68)
        )