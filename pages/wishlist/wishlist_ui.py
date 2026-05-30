# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem,
    QDialog, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor, QColor, QIcon, QPainter
from widget.navbar import Navbar

# ── Palette ───────────────────────────────────────────────────────────
BG           = "#0A1123"
CARD         = "#1A2332"
CARD_HOV     = "#1A2332"
ACCENT       = "#4ADE80"
ACCENT_HOVER = "#4ADE80"
TEXT1        = "#FFFFFF"
TEXT2        = "#8899aa"
BORDER       = "#2A3647"
TAG_BG       = "#2A3647"
DANGER       = "#e74c3c"
DANGER_HOVER = "#c0392b"

class RatingRingWidget(QWidget):
    def __init__(self, value: int, parent=None):
        super().__init__(parent)
        self._value = max(0, min(100, int(value)))
        self.setFixedSize(QSize(48, 48))

    def _ring_color(self) -> QColor:
        if self._value >= 90:
            return QColor("#4ADE80")
        elif self._value >= 75:
            return QColor("#FACC15")
        else:
            return QColor("#e74c3c")

    def paintEvent(self, event):
        from PyQt5.QtGui import QPen, QFont
        size   = min(self.width(), self.height())
        margin = 4
        rect   = self.rect().adjusted(margin, margin, -margin, -margin)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # ── Track (lingkaran abu-abu di belakang) ──────────────────
        pen_track = QPen(QColor("#2A3647"), 4, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen_track)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(rect)

        # ── Arc terisi sesuai persentase ───────────────────────────
        pen_arc = QPen(self._ring_color(), 4, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen_arc)
        # drawArc: sudut dalam 1/16 derajat, mulai dari jam 12 (90°)
        start_angle = 90 * 16
        span_angle  = -int(360 * 16 * self._value / 100)
        p.drawArc(rect, start_angle, span_angle)

        # ── Teks angka di tengah ───────────────────────────────────
        font = QFont("Arial", 11, QFont.Bold)
        p.setFont(font)
        p.setPen(self._ring_color())
        p.drawText(self.rect(), Qt.AlignCenter, str(self._value))

        p.end()
        
class ClickableCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._pressed = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pressed:
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        self._pressed = False
        super().mouseReleaseEvent(event)

# ══════════════════════════════════════════════════════════════════════
#  CUSTOM DIALOG: Konfirmasi Penghapusan
# ══════════════════════════════════════════════════════════════════════
class DeleteConfirmDialog(QDialog):
    """
    Dialog konfirmasi hapus wishlist bergaya dark seperti pada desain.
    Kembalikan True jika user klik 'Ya, Hapus', False jika 'Batal'.
    """

    def __init__(self, nama_game: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        if parent:
            self.setFixedSize(parent.size())

        self._result = False
        self._build_ui(nama_game)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 128))
        p.end()

    def _build_ui(self, nama_game: str):
        # Wrapper dengan shadow
        wrapper = QWidget(self)
        wrapper.setObjectName("dlgWrapper")
        wrapper.setFixedWidth(480)
        wrapper.setStyleSheet(f"""
            QWidget#dlgWrapper {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        wrapper.setGraphicsEffect(shadow)

        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.setAlignment(Qt.AlignCenter)
        outerLayout.addWidget(wrapper)

        innerLayout = QVBoxLayout(wrapper)
        innerLayout.setContentsMargins(40, 36, 40, 32)
        innerLayout.setSpacing(16)

        # Judul
        titleLabel = QLabel("Konfirmasi Penghapusan")
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT1};
                font-size: 16px;
                font-weight: bold;
                font-family: Arial;
            }}
        """)
        innerLayout.addWidget(titleLabel)

        # Pesan
        msgLabel = QLabel(f"Apakah Anda yakin ingin menghapus <b>{nama_game}</b> dari wishlist?")
        msgLabel.setAlignment(Qt.AlignCenter)
        msgLabel.setWordWrap(True)
        msgLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT2};
                font-size: 13px;
                font-family: Arial;
                line-height: 1.5;
            }}
        """)
        innerLayout.addWidget(msgLabel)

        # Tombol
        btnRow = QHBoxLayout()
        btnRow.setSpacing(12)

        btnHapus = QPushButton("Ya, Hapus")
        btnHapus.setFixedHeight(40)
        btnHapus.setCursor(QCursor(Qt.PointingHandCursor))
        btnHapus.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER};
                color: {TEXT1};
                font-size: 13px;
                font-weight: bold;
                font-family: Arial;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {DANGER_HOVER};
            }}
        """)
        btnHapus.clicked.connect(self._on_hapus)

        btnBatal = QPushButton("Batal")
        btnBatal.setFixedHeight(40)
        btnBatal.setCursor(QCursor(Qt.PointingHandCursor))
        btnBatal.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT1};
                font-size: 13px;
                font-weight: bold;
                font-family: Arial;
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {CARD_HOV};
                border: 1px solid {TEXT2};
            }}
        """)
        btnBatal.clicked.connect(self._on_batal)

        btnRow.addWidget(btnHapus)
        btnRow.addWidget(btnBatal)
        innerLayout.addLayout(btnRow)

    def _on_hapus(self):
        self._result = True
        self.accept()

    def _on_batal(self):
        self._result = False
        self.reject()

    def confirmed(self) -> bool:
        return self._result


# ══════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════
class WishlistWindow(QMainWindow):
    delete_requested = pyqtSignal(int, str, str)
    game_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAGER - Wishlist Saya")
        self.setGeometry(0, 0, 1160, 660)
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {BG}; }}
            QWidget#centralwidget {{ background-color: {BG}; }}
        """)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.nav = Navbar(active_page="wishlist")
        self.mainLayout.addWidget(self.nav)

        self._build_content_area()

    # ── Content Area ──────────────────────────────────────────────────
    def _build_content_area(self):
        self.contentArea = QWidget()
        self.contentArea.setObjectName("contentArea")
        self.contentArea.setStyleSheet(f"QWidget#contentArea {{ background-color: {BG}; }}")

        self.contentLayout = QVBoxLayout(self.contentArea)
        self.contentLayout.setContentsMargins(40, 30, 40, 30)
        self.contentLayout.setSpacing(16)

        self.btnKembali = QPushButton(" Kembali")
        self.btnKembali.setIcon(QIcon("assets/icon-back.png"))
        self.btnKembali.setIconSize(QSize(16, 16))
        self.btnKembali.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnKembali.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT2};
                font-size: 13px; font-family: Arial;
                border: none; padding: 0px;
                text-align: left; max-width: 100px;
            }}
            QPushButton:hover {{ color: {TEXT1}; }}
        """)
        self.contentLayout.addWidget(self.btnKembali)

        self.titleLabel = QLabel("Wishlist Saya")
        self.titleLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT1}; font-size: 26px; font-weight: bold; font-family: Arial; }}
        """)
        self.contentLayout.addWidget(self.titleLabel)

        self.subtitleLabel = QLabel("")
        self.subtitleLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 13px; font-family: Arial; }}
        """)
        self.contentLayout.addWidget(self.subtitleLabel)

        self.stackedWidget = QStackedWidget()

        self.pageWithItems = QWidget()
        self.itemsLayout = QVBoxLayout(self.pageWithItems)
        self.itemsLayout.setSpacing(12)
        self.itemsLayout.setContentsMargins(0, 0, 0, 0)
        self.itemsLayout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        self.stackedWidget.addWidget(self.pageWithItems)
        self.stackedWidget.addWidget(self._build_page_empty())
        self.stackedWidget.setCurrentIndex(1)

        # Bungkus stackedWidget dengan ScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.stackedWidget)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {CARD};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ACCENT};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self.contentLayout.addWidget(scroll)
        self.mainLayout.addWidget(self.contentArea)

    # ── Render Wishlist ───────────────────────────────────────────────
    def render_wishlist(self, items: list):
        while self.itemsLayout.count() > 1:
            child = self.itemsLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not items:
            self.stackedWidget.setCurrentIndex(1)
            return

        self.stackedWidget.setCurrentIndex(0)

        spacer_index = self.itemsLayout.count() - 1
        for item in items:
            card = self._build_game_card(item)
            self.itemsLayout.insertWidget(spacer_index, card)
            spacer_index += 1

        self.itemsLayout.insertWidget(spacer_index, self._build_cta_card())

    # ── Game Card ─────────────────────────────────────────────────────
    def _build_game_card(self, item: dict):
        id_wishlist   = item["id_wishlist"]
        nama_game     = item.get("nama_game", "—")
        harga_reguler = item.get("harga_reguler") or 0
        harga_diskon  = item.get("harga_diskon") or harga_reguler
        rating        = item.get("rating") or 0
        tgl           = item.get("tanggal_ditambahkan")
        tgl_str       = tgl.strftime("%d %B %Y").lstrip("0") if tgl else "—"

        id_game = str(item.get("id_game", ""))

        card = ClickableCard()
        card.setObjectName(f"wcard_{id_wishlist}")
        card.setStyleSheet(f"""
            #wcard_{id_wishlist} {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            #wcard_{id_wishlist}:hover {{
                border: 1px solid {ACCENT_HOVER};
            }}
        """)
        card.clicked.connect(lambda checked=False, gid=id_game: self.game_clicked.emit(gid))

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Thumbnail
        url_gambar = item.get("url_gambar") or ""
        thumb = QLabel()
        thumb.setFixedSize(QSize(170, 90))
        thumb.setAlignment(Qt.AlignCenter)

        POSTER_DIR = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "assets", "posters"
        )
        img_path = os.path.join(POSTER_DIR, url_gambar)

        if url_gambar and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(170, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            thumb.setPixmap(pixmap)
        else:
            thumb.setText(f"[ {nama_game} ]")
            thumb.setStyleSheet(f"""
                QLabel {{
                    background-color: {TAG_BG}; color: {TEXT2};
                    font-size: 11px; font-family: Arial; border-radius: 4px;
                }}
            """)
        layout.addWidget(thumb, alignment=Qt.AlignTop)

        # Info game
        infoWidget = QWidget()
        infoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        infoLayout = QVBoxLayout(infoWidget)
        infoLayout.setSpacing(6)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        nameLabel = QLabel(nama_game)
        nameLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT1}; font-size: 17px; font-weight: bold; font-family: Arial; }}
        """)
        infoLayout.addWidget(nameLabel, alignment=Qt.AlignTop)

        # Tag genre
        genres_str = item.get("genres") or ""
        genre_list = [g.strip() for g in genres_str.split(",") if g.strip()][:3]
        if genre_list:
            tagRow = QWidget()
            tagRow.setFixedHeight(28)
            tagLayout = QHBoxLayout(tagRow)
            tagLayout.setSpacing(6)
            tagLayout.setContentsMargins(0, 0, 0, 0)
            for genre in genre_list:
                tag = QLabel(genre)
                tag.setStyleSheet(f"""
                    QLabel {{
                        background-color: {TAG_BG}; color: {TEXT2};
                        font-size: 11px; font-family: Arial;
                        border-radius: 4px; padding: 2px 7px;
                    }}
                """)
                tagLayout.addWidget(tag)
            tagLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            infoLayout.addWidget(tagRow)

        # Harga & rating
        priceRow = QWidget()
        priceLayout = QHBoxLayout(priceRow)
        priceLayout.setSpacing(8)
        priceLayout.setContentsMargins(0, 0, 0, 0)

        ratingRing = RatingRingWidget(int(rating))
        priceLayout.addWidget(ratingRing)

        saleLabel = QLabel(f"Rp {int(harga_diskon):,}".replace(",", "."))
        saleLabel.setStyleSheet(f"""
            QLabel {{ color: {ACCENT}; font-size: 15px; font-weight: bold; font-family: Arial; }}
        """)
        priceLayout.addWidget(saleLabel)
        priceLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        infoLayout.addWidget(priceRow)
        layout.addWidget(infoWidget, alignment=Qt.AlignTop)
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Kolom kanan
        rightCol = QWidget()
        rightColLayout = QVBoxLayout(rightCol)
        rightColLayout.setSpacing(8)
        rightColLayout.setContentsMargins(0, 0, 0, 0)

        dateLabel = QLabel(f"Ditambahkan pada {tgl_str}")
        dateLabel.setAlignment(Qt.AlignRight)
        dateLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 12px; font-family: Arial; }}
        """)
        rightColLayout.addWidget(dateLabel)
        rightColLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        _trash_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets", "trash.png"
        )
        btnDelete = QPushButton()
        btnDelete.setFixedSize(QSize(36, 36))
        btnDelete.setCursor(QCursor(Qt.PointingHandCursor))
        if os.path.exists(_trash_path):
            btnDelete.setIcon(QIcon(QPixmap(_trash_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            btnDelete.setIconSize(QSize(18, 18))
        btnDelete.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(231, 76, 60, 0.1);
                border: 1px solid rgba(231, 76, 60, 0.4); border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {DANGER}; }}
        """)
        btnDelete.clicked.connect(
            lambda _, wid=id_wishlist, nm=nama_game, gid=id_game:
                self.delete_requested.emit(wid, nm, gid)
        )
        rightColLayout.addWidget(btnDelete, alignment=Qt.AlignRight)

        layout.addWidget(rightCol, alignment=Qt.AlignTop)
        return card

    # ── CTA Card ──────────────────────────────────────────────────────
    def _build_cta_card(self):
        self.ctaCard = QWidget()
        self.ctaCard.setObjectName("ctaCard")
        self.ctaCard.setStyleSheet(f"""
            QWidget#ctaCard {{
                background-color: {CARD};
                border: 1px dashed {BORDER};
                border-radius: 8px;
            }}
        """)

        ctaLayout = QVBoxLayout(self.ctaCard)
        ctaLayout.setContentsMargins(32, 24, 32, 24)
        ctaLayout.setSpacing(12)

        ctaText = QLabel("Ingin tambah game lagi pada Wishlist?")
        ctaText.setAlignment(Qt.AlignCenter)
        ctaText.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 13px; font-family: Arial; }}
        """)
        ctaLayout.addWidget(ctaText)

        btnRow = QHBoxLayout()
        btnRow.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btnJelajahiGame1 = QPushButton("Jelajahi Game")
        self.btnJelajahiGame1.setFixedSize(QSize(140, 36))
        self.btnJelajahiGame1.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnJelajahiGame1.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #000000; font-size: 13px;
                font-weight: bold; font-family: Arial; border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        """)
        btnRow.addWidget(self.btnJelajahiGame1)
        btnRow.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        ctaLayout.addLayout(btnRow)
        return self.ctaCard

    # ── Empty State ───────────────────────────────────────────────────
    def _build_page_empty(self):
        self.pageEmpty = QWidget()
        emptyLayout = QVBoxLayout(self.pageEmpty)
        emptyLayout.setSpacing(0)
        emptyLayout.setContentsMargins(0, 0, 0, 0)

        emptyCard = QWidget()
        emptyCard.setObjectName("emptyCard")
        emptyCard.setStyleSheet(f"""
            QWidget#emptyCard {{
                background-color: {CARD};
                border: 1px dashed {BORDER};
                border-radius: 8px;
            }}
        """)

        emptyCardLayout = QVBoxLayout(emptyCard)
        emptyCardLayout.setContentsMargins(40, 60, 40, 60)
        emptyCardLayout.setSpacing(16)

        emptyLabel = QLabel("Wishlist Anda masih kosong")
        emptyLabel.setAlignment(Qt.AlignCenter)
        emptyLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 14px; font-family: Arial; }}
        """)
        emptyCardLayout.addWidget(emptyLabel)

        btnRow = QHBoxLayout()
        btnRow.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btnJelajahiGame2 = QPushButton("Jelajahi Game")
        self.btnJelajahiGame2.setFixedSize(QSize(140, 36))
        self.btnJelajahiGame2.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnJelajahiGame2.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #000000; font-size: 13px;
                font-weight: bold; font-family: Arial; border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        """)
        btnRow.addWidget(self.btnJelajahiGame2)
        btnRow.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        emptyCardLayout.addLayout(btnRow)
        emptyLayout.addWidget(emptyCard)
        emptyLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return self.pageEmpty

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WishlistWindow()
    window.show()
    sys.exit(app.exec_())