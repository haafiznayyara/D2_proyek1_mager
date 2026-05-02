"""
MAGER - Game Detail Page  (profileGame_ui.py)
Terintegrasi dengan profileGame_logic.py
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
    QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QPixmap, QRadialGradient
)

from pages.gameProfile.profileGame_logic import (
    GameDetailLoader, ImageFetcher,
    fmt_price, fmt_number, rating_label,
)

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0d1117"
BG_DARK     = "#161b27"
BG_CARD     = "#1a2035"
BG_ELEM     = "#1e2840"
BG_INPUT    = "#242d45"
BORDER      = "#2a3555"
WHITE       = "#ffffff"
LIGHT       = "#c9d1e0"
MUTED       = "#7b8db0"
DIM         = "#4a5580"
GREEN       = "#00c853"
RED_BTN     = "#8b1a1a"
RED_BTN_BDR = "#c0392b"
DISC_GREEN  = "#1a7a3a"


# ── Clickable Icon ────────────────────────────────────────────────────────────
class ClickableIcon(QLabel):
    clicked = pyqtSignal(bool)

    def __init__(self, img_normal, img_active, parent=None):
        super().__init__(parent)
        self.is_active  = False
        self.img_normal = img_normal
        self.img_active = img_active
        self.update_image()
        self.setCursor(Qt.PointingHandCursor)

    def update_image(self):
        current = self.img_active if self.is_active else self.img_normal
        px = QPixmap(current)
        if px.isNull():
            self.setText("👍" if "like" in self.img_normal else "👎")
            self.setStyleSheet(f"color:{WHITE};font-size:16px;")
        else:
            self.setPixmap(px.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_active = not self.is_active
            self.update_image()
            self.clicked.emit(self.is_active)


# ── Circular Rating ───────────────────────────────────────────────────────────
class RatingCircle(QWidget):
    def __init__(self, value=0, label="—", parent=None):
        super().__init__(parent)
        self.value = value
        self.label = label
        self.setFixedSize(90, 90)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, r = 45, 45, 36

        p.setPen(QPen(QColor(BORDER), 4))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        span = int(self.value / 100 * 360 * 16)
        p.setPen(QPen(QColor(GREEN), 4))
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 90 * 16, -span)

        p.setPen(QPen(QColor(WHITE)))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(QRect(0, 10, 90, 45), Qt.AlignCenter, f"{self.value}%")

        p.setPen(QPen(QColor(GREEN)))
        p.setFont(QFont("Arial", 9))
        p.drawText(QRect(0, 46, 90, 20), Qt.AlignCenter, self.label)


# ── Price Chart ───────────────────────────────────────────────────────────────
class PriceChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Data default (dummy) — diganti via set_data() jika DB punya riwayat
        self._pts: list[QPointF] = []
        self._max_price: float   = 1.0
        self._x_labels: list[str] = []

    def set_data(self, history: list[dict]):
        """
        history: [{"date": "2024-12", "price": 299000}, ...]
        Dipanggil dari GameDetailWindow.load_price_history()
        """
        if not history:
            return
        self._max_price = max(h["price"] for h in history) or 1.0
        self._raw       = history

        # Label sumbu X: ambil setiap ~4 titik supaya tidak penuh
        step = max(1, len(history) // 8)
        self._x_labels = [
            (history[i]["date"] if i < len(history) else "")
            for i in range(0, len(history), step)
        ]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 65, 20, 12, 40
        draw_w = W - pad_l - pad_r
        draw_h = H - pad_t - pad_b

        p.fillRect(0, 0, W, H, QColor(BG_CARD))

        # Grid horizontal
        p.setPen(QPen(QColor(BORDER), 1))
        for i in range(5):
            y = pad_t + draw_h - int(i / 4 * draw_h)
            p.drawLine(pad_l, y, W - pad_r, y)

        # Label Y
        p.setPen(QPen(QColor(MUTED)))
        p.setFont(QFont("Arial", 7))
        for i in range(5):
            y   = pad_t + draw_h - int(i / 4 * draw_h)
            val = int(i / 4 * self._max_price)
            lbl = f"Rp {val//1000}k" if val >= 1000 else f"Rp {val}"
            p.drawText(QRect(0, y - 8, pad_l - 4, 16),
                       Qt.AlignRight | Qt.AlignVCenter, lbl)

        raw = getattr(self, "_raw", [])
        if not raw:
            # Tidak ada data — tampilkan teks
            p.setPen(QPen(QColor(MUTED)))
            p.drawText(QRect(0, 0, W, H), Qt.AlignCenter, "Belum ada riwayat harga")
            return

        n   = len(raw)
        pts = []
        for i, h in enumerate(raw):
            x = pad_l + int(i / max(n - 1, 1) * draw_w)
            y = pad_t + draw_h - int(h["price"] / self._max_price * draw_h)
            pts.append(QPointF(x, y))

        # Label X
        x_labels = self._x_labels
        step      = max(1, n // len(x_labels)) if x_labels else 1
        for idx, lbl in enumerate(x_labels):
            xi = idx * step
            if xi >= len(pts):
                break
            x = int(pts[xi].x())
            p.setPen(QPen(QColor(MUTED)))
            p.drawText(QRect(x - 30, H - pad_b + 4, 60, 20), Qt.AlignCenter, lbl)

        # Area fill
        fill = QPainterPath()
        fill.moveTo(pts[0])
        for pt in pts[1:]:
            fill.lineTo(pt)
        fill.lineTo(pts[-1].x(), pad_t + draw_h)
        fill.lineTo(pts[0].x(), pad_t + draw_h)
        fill.closeSubpath()

        grad = QLinearGradient(0, pad_t, 0, pad_t + draw_h)
        grad.setColorAt(0, QColor(0, 200, 83, 60))
        grad.setColorAt(1, QColor(0, 200, 83, 0))
        p.fillPath(fill, QBrush(grad))

        # Garis
        line = QPainterPath()
        line.moveTo(pts[0])
        for pt in pts[1:]:
            line.lineTo(pt)
        p.setPen(QPen(QColor(GREEN), 2))
        p.setBrush(Qt.NoBrush)
        p.drawPath(line)


# ── GameDetailWindow ──────────────────────────────────────────────────────────
class GameDetailWindow(QWidget):
    back_clicked         = pyqtSignal()
    nav_wishlist_clicked = pyqtSignal()
    nav_profile_clicked  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game: dict     = {}
        self._raw_cover: QPixmap | None = None
        self._loader = GameDetailLoader(self)
        self._loader.game_ready.connect(self._on_game_ready)
        self._loader.history_ready.connect(self.load_price_history)
        self._loader.error.connect(lambda msg: print("[Detail]", msg))
        self._build()

    # ── Public API ────────────────────────────────────────────────────────
    def open_game(self, game_id: int):
        """
        Dipanggil Router ketika card diklik.
        Fetch data dari DB secara async, lalu refresh UI.
        """
        self._loader.load(game_id)

    def load_game(self, game: dict):
        self._game = game
        self._raw_cover = None  # reset cover lama
        self._refresh_ui()

        # ← tambahkan ini: fetch gambar dari URL
        url = game.get("img", "")
        print(f"[DEBUG] URL gambar: '{url}'")
        if url:
            self._fetcher = ImageFetcher(url, self)
            self._fetcher.done.connect(self._on_cover_data)
            self._fetcher.fetch_async()

    def load_price_history(self, history: list):
        """Dipanggil otomatis oleh loader setelah game_ready."""
        self.price_chart.set_data(history)

    # ── Internal: terima data dari loader ────────────────────────────────
    def _on_game_ready(self, game):
        if game is None:
            return
        self.load_game(game)
        # Fetch cover image
        url = game.get("img", "")
        if url:
            self._fetcher = ImageFetcher(url, self)
            self._fetcher.done.connect(self._on_cover_data)
            self._fetcher.fetch_async()

    def _on_cover_data(self, data: bytes):
        print(f"[DEBUG] Data gambar diterima: {len(data)} bytes")
        if not data:
            return
        px = QPixmap()
        px.loadFromData(data)
        print(f"[DEBUG] QPixmap valid: {not px.isNull()}")
        if px.isNull():
            return
        self._raw_cover = px
        self._apply_cover()

    def _apply_cover(self):
        if self._raw_cover is None:
            return
        w = self.lbl_cover.width()
        h = self.lbl_cover.height()
        scaled = self._raw_cover.scaled(
            w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        x = (scaled.width()  - w) // 2
        y = (scaled.height() - h) // 2
        self.lbl_cover.setPixmap(scaled.copy(x, y, w, h))
        self.lbl_cover.setText("")

    def _refresh_ui(self):
        g = self._game
        if not g:
            return

        self.lbl_title.setText(g.get("title", ""))

        # Cover placeholder sementara gambar di-fetch
        ac = g.get("ac", "#333")
        self.lbl_cover.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 #1a0a00, stop:0.5 {ac}, stop:1 #0d1117);"
            f"color:{MUTED};font-size:14px;border-radius:8px;"
        )
        self.lbl_cover.setText(f"[ {g.get('title', 'Cover')} ]")
        self._raw_cover = None  # reset cover lama

        self.lbl_dev.setText(g.get("dev", "-"))
        self.lbl_pub.setText(g.get("pub", "-"))
        self.lbl_release.setText(g.get("release_date", "-"))
        self.lbl_total_reviews.setText(fmt_number(g.get("total_reviews", 0)))
        self.lbl_genre_tag.setText(g.get("genre", ""))
        self.lbl_desc.setText(g.get("description", "-"))

        # Statistik player
        self.lbl_current_player.setText(fmt_number(g.get("current_player", 0)))
        self.lbl_peak_player.setText(fmt_number(g.get("peak_player", 0)))

        # Harga
        price = g.get("price", 0)
        if price == 0:
            self.lbl_price.setText("Gratis")
            self.lbl_old_price.setText("")
            self.lbl_disc.setText("")
        else:
            self.lbl_price.setText(fmt_price(price))
            self.lbl_old_price.setText(fmt_price(int(price * 2)))
            self.lbl_disc.setText("-50%")

        # Platform available
        self.lbl_platform_price.setText(
            fmt_price(price) if price > 0 else "Gratis"
        )

        # Rating circle
        rating = g.get("rating", 0)
        self.ring.value = rating
        self.ring.label = rating_label(rating)
        self.ring.update()

        # Review counts
        self.lbl_review_count.setText(
            f"{fmt_number(g.get('total_reviews', 0))} ulasan pengguna"
        )
        self.lbl_good_count.setText(str(g.get("good_review", 0)))
        self.lbl_bad_count.setText(str(g.get("bad_review", 0)))

    # ── UI Build ──────────────────────────────────────────────────────────
    def _build(self):
        self.setStyleSheet(self._qss())
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addWidget(self._navbar())

        # Back bar
        back_bar = QWidget()
        back_bar.setStyleSheet(f"background:{BG};")
        bb = QHBoxLayout(back_bar)
        bb.setContentsMargins(20, 8, 20, 4)
        btn_back = QPushButton("← Kembali")
        btn_back.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;color:{MUTED};"
            f"font-size:13px;}} QPushButton:hover{{color:{WHITE};}}"
        )
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.back_clicked)
        bb.addWidget(btn_back)
        bb.addStretch()
        vbox.addWidget(back_bar)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background:{BG};border:none;")

        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        cl = QHBoxLayout(content)
        cl.setContentsMargins(20, 8, 20, 24)
        cl.setSpacing(16)
        cl.setAlignment(Qt.AlignTop)

        left = QWidget()
        left.setStyleSheet(f"background:{BG};")
        left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(14)
        ll.addWidget(self._cover_image())
        ll.addWidget(self._game_info())
        ll.addWidget(self._description())
        ll.addWidget(self._price_history())
        ll.addStretch()

        right = self._sidebar()
        right.setFixedWidth(290)

        cl.addWidget(left)
        cl.addWidget(right, alignment=Qt.AlignTop)

        scroll.setWidget(content)
        vbox.addWidget(scroll)

    def _qss(self):
        return f"""
* {{ font-family: Arial; }}
QWidget {{ background: {BG}; color: {WHITE}; }}
QScrollBar:vertical {{
    background: {BG_DARK}; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BG_ELEM}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
QFrame#card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
"""

    def _navbar(self):
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"background:{BG_DARK};border-bottom:1px solid {BORDER};")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(0)

        logo = QLabel("MAGER")
        logo.setStyleSheet(
            f"color:{WHITE};font-size:20px;font-weight:900;letter-spacing:1px;"
        )
        h.addWidget(logo)
        h.addSpacing(24)

        for txt in ["Popular Games", "Cheapest Games"]:
            btn = QPushButton(txt)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton{{background:transparent;border:none;color:{MUTED};"
                f"font-size:13px;padding:8px 14px;}}"
                f"QPushButton:hover{{color:{WHITE};}}"
            )
            h.addWidget(btn)

        h.addStretch()

        search = QLineEdit()
        search.setPlaceholderText("Search games...")
        search.setFixedSize(220, 32)
        search.setStyleSheet(
            f"QLineEdit{{background:{BG_ELEM};border:1px solid {BORDER};"
            f"border-radius:16px;padding:0 16px;color:{WHITE};font-size:13px;}}"
            f"QLineEdit:focus{{border:1px solid {GREEN};}}"
        )
        h.addWidget(search)
        h.addSpacing(10)

        heart = QPushButton("♡")
        heart.setFixedSize(34, 34)
        heart.setStyleSheet(
            f"QPushButton{{background:{BG_ELEM};border:1px solid {BORDER};"
            f"border-radius:17px;color:{MUTED};font-size:15px;}}"
            f"QPushButton:hover{{color:#f06292;border-color:#f06292;}}"
        )
        heart.clicked.connect(self.nav_wishlist_clicked)
        h.addWidget(heart)
        h.addSpacing(8)

        user = QPushButton("👤")
        user.setFixedSize(34, 34)
        user.setStyleSheet(
            f"QPushButton{{background:{BG_ELEM};border:1px solid {BORDER};"
            f"border-radius:17px;color:{MUTED};font-size:14px;}}"
            f"QPushButton:hover{{color:{WHITE};}}"
        )
        user.clicked.connect(self.nav_profile_clicked)
        h.addWidget(user)
        return bar

    def _cover_image(self):
        self.lbl_cover = QLabel("[ Memuat cover... ]")
        self.lbl_cover.setFixedHeight(200)
        self.lbl_cover.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lbl_cover.setAlignment(Qt.AlignCenter)
        self.lbl_cover.setStyleSheet(
            f"background:{BG_CARD};color:{MUTED};font-size:14px;border-radius:8px;"
        )
        return self.lbl_cover

    def _game_info(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        self.lbl_title = QLabel("—")
        self.lbl_title.setStyleSheet(
            f"color:{WHITE};font-size:22px;font-weight:bold;background:transparent;"
        )
        v.addWidget(self.lbl_title)

        tags_row = QHBoxLayout(); tags_row.setSpacing(6)
        self.lbl_genre_tag = QLabel("")
        self.lbl_genre_tag.setStyleSheet(
            f"background:{BG_ELEM};color:{MUTED};font-size:10px;"
            f"padding:3px 9px;border-radius:3px;"
        )
        tags_row.addWidget(self.lbl_genre_tag)
        tags_row.addStretch()
        v.addLayout(tags_row)

        meta = QGridLayout()
        meta.setSpacing(8)
        meta.setContentsMargins(0, 4, 0, 0)

        def meta_block(icon, label):
            bw = QWidget(); bw.setStyleSheet("background:transparent;")
            bv = QVBoxLayout(bw); bv.setContentsMargins(0, 0, 0, 0); bv.setSpacing(2)
            top = QHBoxLayout(); top.setSpacing(5)
            top.addWidget(QLabel(icon))
            lbl_w = QLabel(label)
            lbl_w.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
            top.addWidget(lbl_w); top.addStretch()
            val = QLabel("—")
            val.setStyleSheet(
                f"color:{LIGHT};font-size:13px;font-weight:500;background:transparent;"
            )
            bv.addLayout(top); bv.addWidget(val)
            return bw, val

        b1, self.lbl_dev          = meta_block("👤", "Developer")
        b2, self.lbl_release      = meta_block("📅", "Tanggal Rilis")
        b3, self.lbl_pub          = meta_block("🏢", "Publisher")
        b4, self.lbl_total_reviews= meta_block("⭐", "Total Reviews")

        meta.addWidget(b1, 0, 0); meta.addWidget(b2, 0, 1)
        meta.addWidget(b3, 1, 0); meta.addWidget(b4, 1, 1)
        v.addLayout(meta)
        return w

    def _description(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(8)
        title = QLabel("~ Deskripsi")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        v.addWidget(title)
        self.lbl_desc = QLabel("—")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet(f"color:{LIGHT};font-size:12px;background:transparent;")
        v.addWidget(self.lbl_desc)
        return w

    def _price_history(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(10)
        title = QLabel("~ Riwayat Harga")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        v.addWidget(title)
        self.price_chart = PriceChart()
        v.addWidget(self.price_chart)
        return w

    def _sidebar(self):
        w = QWidget(); w.setStyleSheet(f"background:{BG};")
        v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)
        v.addWidget(self._sidebar_rating())
        v.addWidget(self._sidebar_price())
        v.addWidget(self._sidebar_stats())
        v.addWidget(self._sidebar_available())
        v.addWidget(self._sidebar_comment())
        v.addStretch()
        return w

    def _card_frame(self):
        f = QFrame(); f.setObjectName("card"); return f

    def _sidebar_rating(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(8)
        v.setAlignment(Qt.AlignHCenter)

        self.ring = RatingCircle(0, "—")
        v.addWidget(self.ring, alignment=Qt.AlignHCenter)

        self.lbl_review_count = QLabel("— ulasan pengguna")
        self.lbl_review_count.setStyleSheet(
            f"color:{MUTED};font-size:11px;background:transparent;"
        )
        self.lbl_review_count.setAlignment(Qt.AlignCenter)
        v.addWidget(self.lbl_review_count)

        thumbs = QHBoxLayout()
        thumbs.setSpacing(20)
        thumbs.setAlignment(Qt.AlignHCenter)

        def thumb_block(img_n, img_a, count_attr):
            bw = QWidget(); bw.setStyleSheet("background:transparent;")
            bh = QHBoxLayout(bw); bh.setContentsMargins(0, 0, 0, 0); bh.setSpacing(6)
            ico = ClickableIcon(img_n, img_a)
            ico.setStyleSheet("background:transparent;")
            num = QLabel("0")
            num.setStyleSheet(
                f"color:{LIGHT};font-size:12px;font-weight:bold;background:transparent;"
            )
            setattr(self, count_attr, num)

            def on_click(active):
                cur = int(num.text())
                num.setText(str(cur + 1 if active else max(0, cur - 1)))
            ico.clicked.connect(on_click)
            bh.addWidget(ico); bh.addWidget(num)
            return bw

        thumbs.addWidget(thumb_block(
            "assets/like_outline.png", "assets/like_filled.png", "lbl_good_count"
        ))
        thumbs.addWidget(thumb_block(
            "assets/dislike_outline.png", "assets/dislike_filled.png", "lbl_bad_count"
        ))
        v.addLayout(thumbs)
        return f

    def _sidebar_price(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(6)

        lbl = QLabel("Harga Normal")
        lbl.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        v.addWidget(lbl)

        self.lbl_old_price = QLabel("")
        self.lbl_old_price.setStyleSheet(
            f"color:{DIM};font-size:13px;text-decoration:line-through;background:transparent;"
        )
        v.addWidget(self.lbl_old_price)

        price_row = QHBoxLayout(); price_row.setSpacing(10)

        self.lbl_disc = QLabel("")
        self.lbl_disc.setStyleSheet(
            f"background:{DISC_GREEN};color:{GREEN};font-size:12px;"
            "font-weight:bold;padding:4px 10px;border-radius:4px;"
        )
        self.lbl_disc.setFixedHeight(28)

        self.lbl_price = QLabel("—")
        self.lbl_price.setStyleSheet(
            f"color:{GREEN};font-size:20px;font-weight:bold;background:transparent;"
        )

        price_row.addWidget(self.lbl_disc, alignment=Qt.AlignVCenter)
        price_row.addWidget(self.lbl_price, alignment=Qt.AlignVCenter)
        price_row.addStretch()
        v.addLayout(price_row)

        btn = QPushButton("♥  Hapus dari Wishlist")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton{{background:{RED_BTN};border:1px solid {RED_BTN_BDR};"
            f"border-radius:6px;color:{WHITE};font-size:13px;font-weight:500;}}"
            f"QPushButton:hover{{background:#a02020;}}"
        )
        v.addWidget(btn)
        return f

    def _sidebar_stats(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(8)

        header = QHBoxLayout()
        lbl = QLabel("Statistik Player")
        lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )
        period = QLabel("Dua Minggu Terakhir")
        period.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        header.addWidget(lbl); header.addStretch(); header.addWidget(period)
        v.addLayout(header)

        def stat_row(label, attr, vc=LIGHT):
            row = QWidget()
            row.setStyleSheet(f"background:{BG_ELEM};border-radius:5px;")
            rh = QHBoxLayout(row); rh.setContentsMargins(12, 8, 12, 8)
            l = QLabel(label)
            l.setStyleSheet(f"color:{LIGHT};font-size:12px;background:transparent;")
            r = QLabel("—")
            r.setStyleSheet(
                f"color:{vc};font-size:12px;font-weight:bold;background:transparent;"
            )
            setattr(self, attr, r)
            rh.addWidget(l); rh.addStretch(); rh.addWidget(r)
            return row

        v.addWidget(stat_row("Saat ini",  "lbl_current_player"))
        v.addWidget(stat_row("Tertinggi", "lbl_peak_player", GREEN))
        return f

    def _sidebar_available(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(8)
        lbl = QLabel("Tersedia di")
        lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )
        v.addWidget(lbl)

        row = QWidget()
        row.setStyleSheet(f"background:{BG_ELEM};border-radius:5px;")
        rh = QHBoxLayout(row); rh.setContentsMargins(12, 8, 12, 8)
        p = QLabel("Steam")
        p.setStyleSheet(f"color:{LIGHT};font-size:12px;background:transparent;")
        self.lbl_platform_price = QLabel("—")
        self.lbl_platform_price.setStyleSheet(
            f"color:{GREEN};font-size:12px;font-weight:bold;background:transparent;"
        )
        rh.addWidget(p); rh.addStretch(); rh.addWidget(self.lbl_platform_price)
        v.addWidget(row)
        return f

    def _sidebar_comment(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(8)
        lbl = QLabel("Komentar")
        lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )
        v.addWidget(lbl)

        row = QHBoxLayout(); row.setSpacing(6)
        inp = QLineEdit()
        inp.setPlaceholderText("Tulis komentar Anda...")
        inp.setFixedHeight(36)
        inp.setStyleSheet(
            f"QLineEdit{{background:{BG_INPUT};border:1px solid {BORDER};"
            f"border-radius:5px;padding:0 10px;color:{WHITE};font-size:12px;}}"
            f"QLineEdit:focus{{border:1px solid {GREEN};}}"
        )
        send = QPushButton("Kirim")
        send.setFixedSize(80, 36)
        send.setCursor(Qt.PointingHandCursor)
        send.setStyleSheet(
            f"QPushButton{{background:{GREEN};border:none;border-radius:5px;"
            f"color:#0d1117;font-size:12px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#00a844;}}"
        )
        row.addWidget(inp); row.addWidget(send)
        v.addLayout(row)
        return f