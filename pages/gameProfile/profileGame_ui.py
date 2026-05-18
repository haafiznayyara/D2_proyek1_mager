"""
MAGER - Game Detail Page  (profileGame_ui.py)
Terintegrasi dengan profileGame_logic.py
"""

import os
from widget.navbar import Navbar
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
    QSizePolicy, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QPixmap, QRadialGradient
)

from pages.gameProfile.profileGame_logic import (
    GameDetailLoader, ImageFetcher, ReviewSubmitter,
    fmt_price, fmt_number, rating_label,
)

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0A1123"
BG_DARK     = "#0A1123"
BG_CARD     = "#1A2332"
BG_ELEM     = "#1A2332"
BG_INPUT    = "#0d1829"
BORDER      = "#2A3647"
WHITE       = "#FFFFFF"
LIGHT       = "#c9d1e0"
MUTED       = "#7b8db0"
DIM         = "#4a5580"
GREEN       = "#4ADE80"
DISC_GREEN  = "#4ADE80"
RED_BTN     = "#8b1a1a"
RED_BTN_BDR = "#c0392b"
ACCENT_BLUE = "#3d85c8"

POSTER_DIR = "assets/posters"


def _asset(name):
    base = os.path.dirname(os.path.abspath(__file__))
    root = base
    while not os.path.exists(os.path.join(root, "assets")):
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    return os.path.join(root, "assets", name)


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
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._pts: list[QPointF] = []
        self._max_price: float   = 1.0
        self._x_labels: list[str] = []
        self._raw: list[dict]    = []

    def set_data(self, history: list[dict]):
        if not history:
            return
            
        # 1. Cari harga tertinggi untuk batas atas grafik (Sumbu Y)
        self._max_price = max(h["price"] for h in history) or 1.0
        self._raw       = history
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
        p.setPen(QPen(QColor(BORDER), 1))
        for i in range(5):
            y = pad_t + draw_h - int(i / 4 * draw_h)
            p.drawLine(pad_l, y, W - pad_r, y)

        p.setPen(QPen(QColor(MUTED)))
        p.setFont(QFont("Arial", 7))
        for i in range(5):
            y   = pad_t + draw_h - int(i / 4 * draw_h)
            val = int(i / 4 * self._max_price)
            lbl = f"Rp {val//1000}k" if val >= 1000 else f"Rp {val}"
            p.drawText(QRect(0, y - 8, pad_l - 4, 16),
                       Qt.AlignRight | Qt.AlignVCenter, lbl)

        raw = self._raw
        if not raw:
            p.setPen(QPen(QColor(MUTED)))
            p.drawText(QRect(0, 0, W, H), Qt.AlignCenter, "Belum ada riwayat harga")
            return

        n   = len(raw)
        pts = []
        for i, h in enumerate(raw):
            x = pad_l + int(i / max(n - 1, 1) * draw_w)
            y = pad_t + draw_h - int(h["price"] / self._max_price * draw_h)
            pts.append(QPointF(x, y))

        step = max(1, n // 15) # Maksimal tampilkan berapa label agar tidak dempet
        p.setPen(QPen(QColor(MUTED)))
        
        for i in range(0, n, step):
            x = int(pts[i].x())
            
            # Ambil data tanggal langsung dari raw data
            # Gunakan key "tanggal" atau "date" sesuai yang ada di databasemu
            raw_date = raw[i].get("tanggal") or raw[i].get("date", "")
            lbl = str(raw_date)[:10]
            
            # Lebar kotak diperbesar dari 60 jadi 90 (x - 45, width 90)
            # Ini mencegah teks YYYY-MM-DD terpotong jadi 024-...
            p.drawText(QRect(x - 45, H - pad_b + 4, 90, 20), Qt.AlignCenter, lbl)

        fill = QPainterPath()
        fill.moveTo(pts[0])
        for pt in pts[1:]: fill.lineTo(pt)
        fill.lineTo(pts[-1].x(), pad_t + draw_h)
        fill.lineTo(pts[0].x(), pad_t + draw_h)
        fill.closeSubpath()
        grad = QLinearGradient(0, pad_t, 0, pad_t + draw_h)
        grad.setColorAt(0, QColor(0, 200, 83, 60))
        grad.setColorAt(1, QColor(0, 200, 83, 0))
        p.fillPath(fill, QBrush(grad))

        line = QPainterPath()
        line.moveTo(pts[0])
        for pt in pts[1:]: line.lineTo(pt)
        p.setPen(QPen(QColor(GREEN), 2))
        p.setBrush(Qt.NoBrush)
        p.drawPath(line)


# ── Review Card ───────────────────────────────────────────────────────────────
class ReviewCard(QFrame):
    """Card yang menampilkan satu review dengan 3 aspek."""

    ASPECT_META = [
        ("", "Gameplay",  "gameplay"),
        ("", "Cerita",    "cerita"),
        ("", "Grafik",    "grafik"),
    ]

    def __init__(self, review: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("reviewCard")
        self.setStyleSheet(f"""
            QFrame#reviewCard {{
                background: {BG_ELEM};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 14)
        v.setSpacing(10)

        # ── Header: avatar placeholder + username ──────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        avatar = QLabel(review["username"][0].upper() if review["username"] else "?")
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background:{ACCENT_BLUE};color:{WHITE};font-size:14px;"
            f"font-weight:bold;border-radius:17px;"
        )

        username_lbl = QLabel(review["username"])
        username_lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )

        header.addWidget(avatar)
        header.addWidget(username_lbl)
        header.addStretch()
        v.addLayout(header)

        # ── Divider ────────────────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        v.addWidget(div)

        # ── 3 aspek ────────────────────────────────────────────────────────
        has_any = False
        for icon, label, key in self.ASPECT_META:
            text = (review.get(key) or "").strip()
            if not text:
                continue
            has_any = True

            aspect_row = QVBoxLayout()
            aspect_row.setSpacing(3)

            # Label aspek
            lbl_header = QLabel(f"{icon}  {label}")
            lbl_header.setStyleSheet(
                f"color:{MUTED};font-size:10px;font-weight:bold;"
                f"text-transform:uppercase;letter-spacing:1px;background:transparent;"
            )
            aspect_row.addWidget(lbl_header)

            # Teks review
            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            lbl_text.setStyleSheet(
                f"color:{LIGHT};font-size:12px;line-height:150%;background:transparent;"
            )
            aspect_row.addWidget(lbl_text)
            v.addLayout(aspect_row)

        if not has_any:
            empty = QLabel("— Tidak ada teks review —")
            empty.setStyleSheet(f"color:{DIM};font-size:11px;background:transparent;")
            v.addWidget(empty)


# ── GameDetailWindow ──────────────────────────────────────────────────────────
class GameDetailWindow(QWidget):
    back_clicked         = pyqtSignal()
    nav_wishlist_clicked = pyqtSignal()
    nav_profile_clicked  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game: dict            = {}
        self._raw_cover: QPixmap | None = None
        self._current_user_id: int  = 1

        self._loader = GameDetailLoader(self)
        self._loader.game_ready.connect(self._on_game_ready)
        self._loader.history_ready.connect(self.load_price_history)
        self._loader.genre_ready.connect(self.load_genres)
        self._loader.reviews_ready.connect(self.load_reviews)
        self._loader.error.connect(lambda msg: print("[Detail]", msg))

        self._submitter = ReviewSubmitter(self)
        self._submitter.done.connect(self._on_review_submitted)

        self._build()

    # ── Public API ────────────────────────────────────────────────────────
    def open_game(self, game_id: int):
        self._loader.load(game_id)

    def set_user_id(self, user_id: int):
        """Set ID user yang sedang login (untuk submit review)."""
        self._current_user_id = user_id

    def load_game(self, game: dict):
        self._game = game
        self._raw_cover = None
        self._refresh_ui()
        self._load_cover(game)
        genres = game.get("genres") or game.get("tags") or (
            [game["genre"]] if game.get("genre") else []
        )
        self.load_genres(genres)

    def load_price_history(self, history: list):
        self.price_chart.set_data(history)

    def load_genres(self, genres: list):
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not genres:
            ph = QLabel("—")
            ph.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
            self.tags_layout.addWidget(ph)
        else:
            for genre in genres:
                pill = QLabel(genre)
                pill.setStyleSheet(
                    f"background:{BG_ELEM}; color:{MUTED}; font-size:10px;"
                    f"padding:3px 9px; border-radius:3px; border:1px solid {BORDER};"
                )
                self.tags_layout.addWidget(pill)
        self.tags_layout.addStretch()

    def load_reviews(self, reviews: list):
        """Hapus semua item (widget + spacer) lalu render ulang review card."""
        print(f"[load_reviews] dipanggil, jumlah review: {len(reviews)}")

        # Hapus SEMUA item: widget maupun spacer/stretch
        while self._reviews_layout.count():
            item = self._reviews_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not reviews:
            empty = QLabel("Belum ada review untuk game ini.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color:{MUTED};font-size:12px;padding:20px;background:transparent;"
            )
            self._reviews_layout.addWidget(empty)
        else:
            for rv in reviews:
                print(f"  review dari: {rv.get('username')}")
                card = ReviewCard(rv)
                self._reviews_layout.addWidget(card)

        self._reviews_layout.addStretch()

    # ── Cover loading ─────────────────────────────────────────────────────
    def _load_cover(self, game: dict):
        url = game.get("img", "")
        if not url:
            return
        filename  = os.path.basename(url.split("?")[0])
        local_path = os.path.join(POSTER_DIR, filename)
        if os.path.isfile(local_path):
            px = QPixmap(local_path)
            if not px.isNull():
                self._raw_cover = px
                self._apply_cover()
                return
        self._fetcher = ImageFetcher(url, self)
        self._fetcher.done.connect(self._on_cover_data)
        self._fetcher.fetch_async()

    def _on_game_ready(self, game):
        if game is None: return
        self.load_game(game)

    def _on_cover_data(self, data: bytes):
        if not data: return
        px = QPixmap()
        px.loadFromData(data)
        if px.isNull(): return
        self._raw_cover = px
        self._apply_cover()

    def _apply_cover(self):
        if self._raw_cover is None: return
        w = self.lbl_cover.width()
        h = self.lbl_cover.height()
        if w <= 0 or h <= 0: return
        scaled = self._raw_cover.scaled(
            w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        x = (scaled.width()  - w) // 2
        y = (scaled.height() - h) // 2
        self.lbl_cover.setPixmap(scaled.copy(x, y, w, h))
        self.lbl_cover.setStyleSheet("border-radius:10px;")
        self.lbl_cover.setText("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._raw_cover:
            self._apply_cover()

    def _refresh_ui(self):
        g = self._game
        if not g: return

        self.lbl_title.setText(g.get("title", ""))
        ac = g.get("ac", "#333")
        self.lbl_cover.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 #1a0a00, stop:0.5 {ac}, stop:1 #0d1117);"
            f"color:{MUTED};font-size:13px;border-radius:10px;"
        )
        self.lbl_cover.setText(f"[ {g.get('title', 'Cover')} ]")
        self._raw_cover = None

        self.lbl_dev.setText(g.get("dev", "-"))
        self.lbl_pub.setText(g.get("pub", "-"))
        self.lbl_release.setText(g.get("release_date", "-"))
        self.lbl_total_reviews.setText(fmt_number(g.get("total_reviews", 0)))
        self.lbl_desc.setText(g.get("description", "-"))
        self.lbl_current_player.setText(fmt_number(g.get("current_player", 0)))
        self.lbl_peak_player.setText(fmt_number(g.get("peak_player", 0)))

        price = g.get("price", 0)
        if price == 0:
            self.lbl_price.setText("Gratis")
            self.lbl_old_price.hide()
            self.lbl_disc.hide()
        else:
            self.lbl_price.setText(fmt_price(price))
            self.lbl_old_price.setText(fmt_price(int(price * 2)))
            self.lbl_old_price.show()
            self.lbl_disc.setText("-50%")
            self.lbl_disc.show()

        self.lbl_platform_price.setText(fmt_price(price) if price > 0 else "Gratis")

        rating = g.get("rating", 0)
        self.ring.value = rating
        self.ring.label = rating_label(rating)
        self.ring.update()

        self.lbl_review_count.setText(
            f"{fmt_number(g.get('total_reviews', 0))} ulasan pengguna"
        )
        self.lbl_good_count.setText(str(g.get("good_review", 0)))
        self.lbl_bad_count.setText(str(g.get("bad_review", 0)))

    # ── Submit handler ────────────────────────────────────────────────────
    def _on_submit_review(self):
        game_id = self._game.get("id")
        if not game_id:
            return

        gameplay = self._inp_gameplay.toPlainText().strip()
        cerita   = self._inp_cerita.toPlainText().strip()
        grafik   = self._inp_grafik.toPlainText().strip()

        if not any([gameplay, cerita, grafik]):
            # Setidaknya satu aspek harus diisi
            self._review_status.setText("⚠  Isi minimal satu aspek review.")
            self._review_status.setStyleSheet(
                f"color:#e8b84b;font-size:11px;background:transparent;"
            )
            return

        self._btn_submit_review.setEnabled(False)
        self._btn_submit_review.setText("Menyimpan...")
        self._review_status.setText("")

        self._submitter.submit(
            game_id, self._current_user_id,
            gameplay, cerita, grafik
        )

    def _on_review_submitted(self, ok: bool):
        self._btn_submit_review.setEnabled(True)
        self._btn_submit_review.setText("Kirim Review")

        if ok:
            self._inp_gameplay.clear()
            self._inp_cerita.clear()
            self._inp_grafik.clear()
            self._review_status.setText("✓  Review berhasil disimpan!")
            self._review_status.setStyleSheet(
                f"color:{GREEN};font-size:11px;background:transparent;"
            )
            # Delay 300ms sebelum reload agar sinyal submit selesai dulu
            game_id = self._game.get("id")
            if game_id:
                QTimer.singleShot(300, lambda: self._loader.load(game_id))
        else:
            self._review_status.setText("✗  Gagal menyimpan review, coba lagi.")
            self._review_status.setStyleSheet(
                f"color:#e84b4b;font-size:11px;background:transparent;"
            )

    # ── UI Build ──────────────────────────────────────────────────────────
    def _build(self):
        self.setStyleSheet(self._qss())
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.nav = Navbar(active_page="")
        self.nav.wishlist_clicked.connect(self.nav_wishlist_clicked)
        self.nav.profile_clicked.connect(self.nav_profile_clicked)
        vbox.addWidget(self.nav)

        # Back bar
        back_bar = QWidget()
        back_bar.setStyleSheet(f"background:{BG};")
        bb = QHBoxLayout(back_bar)
        bb.setContentsMargins(24, 10, 24, 6)
        btn_back = QPushButton("← Kembali")
        btn_back.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;color:{MUTED};"
            f"font-size:13px;padding:4px 0;}} QPushButton:hover{{color:{WHITE};}}"
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
        cl.setContentsMargins(24, 10, 24, 32)
        cl.setSpacing(20)
        cl.setAlignment(Qt.AlignTop)

        left = QWidget()
        left.setStyleSheet(f"background:{BG};")
        left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(16)
        ll.addWidget(self._cover_image())
        ll.addWidget(self._game_info())
        ll.addWidget(self._description())
        ll.addWidget(self._price_history())
        ll.addWidget(self._review_input_section())   # ← Form review
        ll.addWidget(self._review_list_section())    # ← Daftar review
        ll.addStretch()

        right = self._sidebar()
        right.setFixedWidth(295)

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
    background: {DIM}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
QFrame#card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QTextEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {WHITE};
    font-size: 12px;
    padding: 6px 10px;
}}
QTextEdit:focus {{ border: 1px solid {GREEN}; }}
"""

    def _cover_image(self):
        self.lbl_cover = QLabel("[ Memuat cover... ]")
        self.lbl_cover.setFixedHeight(220)
        self.lbl_cover.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lbl_cover.setAlignment(Qt.AlignCenter)
        self.lbl_cover.setScaledContents(False)
        self.lbl_cover.setStyleSheet(
            f"background:{BG_CARD};color:{MUTED};font-size:13px;border-radius:10px;"
        )
        return self.lbl_cover

    def _game_info(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        self.lbl_title = QLabel("—")
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet(
            f"color:{WHITE};font-size:22px;font-weight:bold;background:transparent;"
        )
        v.addWidget(self.lbl_title)

        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background:transparent;")
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(6)
        self.tags_layout.addStretch()
        v.addWidget(self.tags_container)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)

        meta = QGridLayout()
        meta.setSpacing(10)
        meta.setContentsMargins(0, 2, 0, 0)
        meta.setColumnStretch(0, 1)
        meta.setColumnStretch(1, 1)

        def meta_block(icon_path: str, label: str):
            bw = QWidget(); bw.setStyleSheet("background:transparent;")
            bv = QVBoxLayout(bw); bv.setContentsMargins(0, 0, 0, 0); bv.setSpacing(3)
            top = QHBoxLayout(); top.setSpacing(6)
            ico_lbl = QLabel()
            ico_lbl.setStyleSheet("background:transparent;")
            px = QPixmap(icon_path)
            if not px.isNull():
                ico_lbl.setPixmap(px.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                ico_lbl.setText(icon_path)
                ico_lbl.setStyleSheet("background:transparent; font-size:12px;")
            top.addWidget(ico_lbl)
            lbl_w = QLabel(label)
            lbl_w.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
            top.addWidget(lbl_w)
            top.addStretch()
            val = QLabel("—")
            val.setWordWrap(True)
            val.setStyleSheet(
                f"color:{LIGHT};font-size:12px;font-weight:500;background:transparent;"
            )
            bv.addLayout(top)
            bv.addWidget(val)
            return bw, val

        b1, self.lbl_dev           = meta_block(_asset("developer-publisher.png"), "Developer")
        b2, self.lbl_release       = meta_block(_asset("calendar.png"),            "Tanggal Rilis")
        b3, self.lbl_pub           = meta_block(_asset("developer-publisher.png"), "Publisher")
        b4, self.lbl_total_reviews = meta_block(_asset("reviews.png"),             "Total Reviews")

        meta.addWidget(b1, 0, 0); meta.addWidget(b2, 0, 1)
        meta.addWidget(b3, 1, 0); meta.addWidget(b4, 1, 1)
        v.addLayout(meta)
        return w

    def _description(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w); v.setContentsMargins(18, 16, 18, 16); v.setSpacing(10)
        title = QLabel("Deskripsi")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        v.addWidget(title)
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)
        self.lbl_desc = QLabel("—")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.lbl_desc.setStyleSheet(
            f"color:{LIGHT};font-size:12px;line-height:160%;background:transparent;"
        )
        self.lbl_desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v.addWidget(self.lbl_desc)
        return w

    def _price_history(self):
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w); v.setContentsMargins(18, 16, 18, 16); v.setSpacing(10)
        title = QLabel("Riwayat Harga")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        v.addWidget(title)
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)
        self.price_chart = PriceChart()
        v.addWidget(self.price_chart)
        return w
    
    def load_price_history(self, history: list[dict]):
        self.price_chart.set_data(history)

    def _review_input_section(self):
        """Form untuk menulis review dengan 3 aspek: Gameplay, Cerita, Grafik."""
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w)
        v.setContentsMargins(18, 16, 18, 18)
        v.setSpacing(14)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("✏  Tulis Review Kamu")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        subtitle = QLabel("Isi minimal satu aspek")
        subtitle.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(subtitle)
        v.addLayout(header_row)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)

        # ── 3 input aspek ──────────────────────────────────────────────────
        aspects = [
            ("Gameplay",  "_inp_gameplay",
             "Bagaimana mekanik, kontrol, dan keseruan gameplay-nya?"),
            ("Cerita",    "_inp_cerita",
             "Bagaimana alur cerita, karakter, dan narasinya?"),
            ("Grafik",    "_inp_grafik",
             "Bagaimana visual, art style, dan kualitas grafisnya?"),
        ]

        for label_text, attr, placeholder in aspects:
            asp_v = QVBoxLayout()
            asp_v.setSpacing(5)

            asp_label = QLabel(label_text)
            asp_label.setStyleSheet(
                f"color:{MUTED};font-size:11px;font-weight:bold;"
                f"background:transparent;"
            )
            asp_v.addWidget(asp_label)

            inp = QTextEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(68)
            inp.setStyleSheet(
                f"QTextEdit{{background:{BG_INPUT};border:1px solid {BORDER};"
                f"border-radius:6px;color:{WHITE};font-size:12px;padding:6px 10px;}}"
                f"QTextEdit:focus{{border:1px solid {GREEN};}}"
            )
            setattr(self, attr, inp)
            asp_v.addWidget(inp)
            v.addLayout(asp_v)

        # ── Status label + tombol kirim ────────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self._review_status = QLabel("")
        self._review_status.setStyleSheet(
            f"color:{GREEN};font-size:11px;background:transparent;"
        )
        bottom_row.addWidget(self._review_status)
        bottom_row.addStretch()

        self._btn_submit_review = QPushButton("Kirim Review")
        self._btn_submit_review.setFixedSize(120, 36)
        self._btn_submit_review.setCursor(Qt.PointingHandCursor)
        self._btn_submit_review.setStyleSheet(
            f"QPushButton{{background:{GREEN};border:none;border-radius:6px;"
            f"color:#0d1117;font-size:12px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#00c853;}}"
            f"QPushButton:disabled{{background:{DIM};color:{MUTED};}}"
        )
        self._btn_submit_review.clicked.connect(self._on_submit_review)
        bottom_row.addWidget(self._btn_submit_review)

        v.addLayout(bottom_row)
        return w

    def _review_list_section(self):
        """Section yang menampilkan semua review yang sudah ada."""
        w = QFrame(); w.setObjectName("card")
        v = QVBoxLayout(w)
        v.setContentsMargins(18, 16, 18, 18)
        v.setSpacing(14)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("💬  Semua Review")
        title.setStyleSheet(
            f"color:{WHITE};font-size:14px;font-weight:bold;background:transparent;"
        )
        header_row.addWidget(title)
        header_row.addStretch()
        v.addLayout(header_row)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)

        # Container untuk list review (di-update oleh load_reviews)
        self._reviews_container = QWidget()
        self._reviews_container.setStyleSheet("background:transparent;")
        self._reviews_layout = QVBoxLayout(self._reviews_container)
        self._reviews_layout.setContentsMargins(0, 0, 0, 0)
        self._reviews_layout.setSpacing(10)

        # Placeholder awal
        loading = QLabel("Memuat review...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet(
            f"color:{MUTED};font-size:12px;padding:16px;background:transparent;"
        )
        self._reviews_layout.addWidget(loading)
        self._reviews_layout.addStretch()

        v.addWidget(self._reviews_container)
        return w

    # ── Sidebar ───────────────────────────────────────────────────────────
    def _sidebar(self):
        w = QWidget(); w.setStyleSheet(f"background:{BG};")
        v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(14)
        v.addWidget(self._sidebar_rating())
        v.addWidget(self._sidebar_price())
        v.addWidget(self._sidebar_stats())
        v.addWidget(self._sidebar_available())
        v.addStretch()
        return w

    def _card_frame(self):
        f = QFrame(); f.setObjectName("card"); return f

    def _sidebar_rating(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 18, 16, 18); v.setSpacing(10)
        v.setAlignment(Qt.AlignHCenter)

        self.ring = RatingCircle(0, "—")
        v.addWidget(self.ring, alignment=Qt.AlignHCenter)

        self.lbl_review_count = QLabel("— ulasan pengguna")
        self.lbl_review_count.setWordWrap(True)
        self.lbl_review_count.setStyleSheet(
            f"color:{MUTED};font-size:11px;background:transparent;"
        )
        self.lbl_review_count.setAlignment(Qt.AlignCenter)
        v.addWidget(self.lbl_review_count)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;")
        v.addWidget(div)

        thumbs = QHBoxLayout()
        thumbs.setSpacing(24)
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
            def on_click(active, _num=num):
                cur = int(_num.text())
                _num.setText(str(cur + 1 if active else max(0, cur - 1)))
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
        v = QVBoxLayout(f); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(6)
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
            f"background:{DISC_GREEN};color:#0d1117;font-size:12px;"
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
        v.addSpacing(4)

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
        v = QVBoxLayout(f); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        header = QHBoxLayout()
        lbl = QLabel("Statistik Player")
        lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )
        period = QLabel("Dua Minggu Terakhir")
        period.setStyleSheet(f"color:{MUTED};font-size:10px;background:transparent;")
        header.addWidget(lbl); header.addStretch(); header.addWidget(period)
        v.addLayout(header)

        def stat_row(label, attr, vc=LIGHT):
            row = QWidget()
            row.setStyleSheet(f"background:{BG_ELEM};border-radius:6px;")
            rh = QHBoxLayout(row); rh.setContentsMargins(12, 9, 12, 9)
            l = QLabel(label)
            l.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
            r = QLabel("—")
            r.setStyleSheet(
                f"color:{vc};font-size:12px;font-weight:bold;background:transparent;"
            )
            setattr(self, attr, r)
            rh.addWidget(l); rh.addStretch(); rh.addWidget(r)
            return row

        v.addWidget(stat_row("Pemain Saat Ini", "lbl_current_player"))
        v.addWidget(stat_row("Puncak Tertinggi", "lbl_peak_player", GREEN))
        return f

    def _sidebar_available(self):
        f = self._card_frame()
        v = QVBoxLayout(f); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        lbl = QLabel("Tersedia di")
        lbl.setStyleSheet(
            f"color:{WHITE};font-size:13px;font-weight:bold;background:transparent;"
        )
        v.addWidget(lbl)
        row = QWidget()
        row.setStyleSheet(f"background:{BG_ELEM};border-radius:6px;")
        rh = QHBoxLayout(row); rh.setContentsMargins(12, 9, 12, 9)
        p = QLabel("Steam")
        p.setStyleSheet(f"color:{LIGHT};font-size:12px;background:transparent;")
        self.lbl_platform_price = QLabel("—")
        self.lbl_platform_price.setStyleSheet(
            f"color:{GREEN};font-size:12px;font-weight:bold;background:transparent;"
        )
        rh.addWidget(p); rh.addStretch(); rh.addWidget(self.lbl_platform_price)
        v.addWidget(row)
        return f