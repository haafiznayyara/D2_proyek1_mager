# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor
from widget.navbar import Navbar

# ── Palette (Disamakan dengan cardGame.py & global app) ───────────────────
BG           = "#0A1123"  # Background utama aplikasi
CARD         = "#1A2332"
CARD_HOV     = "#1e2a42"
ACCENT       = "#39d353"
ACCENT_HOVER = "#2ea84a"
TEXT1        = "#e8eaf0"
TEXT2        = "#8899aa"
BORDER       = "#1e3a50"
TAG_BG       = "#162840"

class WishlistWindow(QMainWindow):
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

        # ===== PENGGUNAAN WIDGET NAVBAR =====
        self.nav = Navbar(active_page="wishlist")
        self.mainLayout.addWidget(self.nav)

        # Konten Utama
        self._build_content_area()

    # ===== CONTENT AREA =====
    def _build_content_area(self):
        self.contentArea = QWidget()
        self.contentArea.setObjectName("contentArea")
        self.contentArea.setStyleSheet(f"QWidget#contentArea {{ background-color: {BG}; }}")

        contentLayout = QVBoxLayout(self.contentArea)
        contentLayout.setContentsMargins(40, 30, 40, 30)
        contentLayout.setSpacing(16)

        # Tombol Kembali
        self.btnKembali = QPushButton("← Kembali")
        self.btnKembali.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnKembali.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT2};
                font-size: 13px;
                font-family: Arial;
                border: none;
                padding: 0px;
                text-align: left;
                max-width: 100px;
            }}
            QPushButton:hover {{ color: {TEXT1}; }}
        """)
        contentLayout.addWidget(self.btnKembali)

        # Judul halaman
        self.titleLabel = QLabel("Wishlist Saya")
        self.titleLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT1};
                font-size: 26px;
                font-weight: bold;
                font-family: Arial;
            }}
        """)
        contentLayout.addWidget(self.titleLabel)

        # Subjudul / jumlah game
        self.subtitleLabel = QLabel("Anda memiliki 2 game dalam wishlist")
        self.subtitleLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT2};
                font-size: 13px;
                font-family: Arial;
            }}
        """)
        contentLayout.addWidget(self.subtitleLabel)

        # Stacked Widget: kosong vs berisi
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self._build_page_with_items())   # index 0
        self.stackedWidget.addWidget(self._build_page_empty())         # index 1
        self.stackedWidget.setCurrentIndex(0)

        contentLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.contentArea)

    # ===== PAGE 0: Ada isi (berisi game) =====
    def _build_page_with_items(self):
        self.pageWithItems = QWidget()
        itemsLayout = QVBoxLayout(self.pageWithItems)
        itemsLayout.setSpacing(12)
        itemsLayout.setContentsMargins(0, 0, 0, 0)

        itemsLayout.addWidget(self._build_game_card_1())
        itemsLayout.addWidget(self._build_game_card_2())
        itemsLayout.addWidget(self._build_cta_card())
        itemsLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return self.pageWithItems

    def _build_game_card_1(self):
        """Card: Cyberpunk 2077"""
        card = QWidget()
        card.setObjectName("card1")
        card.setStyleSheet(f"""
            QWidget#card1 {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QWidget#card1:hover {{ border: 1px solid {ACCENT_HOVER}; }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Thumbnail
        thumb = QLabel("[ Cyberpunk 2077 ]")
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setFixedSize(QSize(170, 90))
        thumb.setStyleSheet(f"""
            QLabel {{
                background-color: {TAG_BG};
                color: {TEXT2};
                font-size: 11px;
                font-family: Arial;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(thumb)

        # Info game
        infoWidget = QWidget()
        infoLayout = QVBoxLayout(infoWidget)
        infoLayout.setSpacing(6)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        nameLabel = QLabel("Cyberpunk 2077")
        nameLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT1}; font-size: 17px; font-weight: bold; font-family: Arial; }}
        """)
        infoLayout.addWidget(nameLabel)

        # Tags
        tagsWidget = QWidget()
        tagsLayout = QHBoxLayout(tagsWidget)
        tagsLayout.setSpacing(6)
        tagsLayout.setContentsMargins(0, 0, 0, 0)
        tag_style = f"""
            QLabel {{
                background-color: {TAG_BG}; color: {TEXT2}; font-size: 11px;
                font-family: Arial; border-radius: 4px; padding: 2px 8px;
                border: 1px solid {BORDER};
            }}
        """
        for tag_text in ["Action", "RPG", "Open World"]:
            t = QLabel(tag_text)
            t.setStyleSheet(tag_style)
            tagsLayout.addWidget(t)
        tagsLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        infoLayout.addWidget(tagsWidget)

        # Harga
        priceRow = QWidget()
        priceLayout = QHBoxLayout(priceRow)
        priceLayout.setSpacing(8)
        priceLayout.setContentsMargins(0, 0, 0, 0)

        rating1 = QLabel("86")
        rating1.setFixedSize(QSize(44, 44))
        rating1.setAlignment(Qt.AlignCenter)
        rating1.setStyleSheet(f"""
            QLabel {{
                background-color: transparent; color: {ACCENT}; font-size: 12px;
                font-weight: bold; font-family: Arial; border: 3px solid {ACCENT}; border-radius: 22px;
            }}
        """)
        priceLayout.addWidget(rating1)

        discount1 = QLabel("-20%")
        discount1.setStyleSheet(f"""
            QLabel {{
                background-color: {ACCENT}; color: #000000; font-size: 12px;
                font-weight: bold; font-family: Arial; border-radius: 4px; padding: 2px 6px;
            }}
        """)
        priceLayout.addWidget(discount1)

        origPrice1 = QLabel("Rp 499.999")
        origPrice1.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 12px; font-family: Arial; text-decoration: line-through; }}
        """)
        priceLayout.addWidget(origPrice1)

        salePrice1 = QLabel("Rp 399.999")
        salePrice1.setStyleSheet(f"""
            QLabel {{ color: {ACCENT}; font-size: 15px; font-weight: bold; font-family: Arial; }}
        """)
        priceLayout.addWidget(salePrice1)
        priceLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        infoLayout.addWidget(priceRow)
        layout.addWidget(infoWidget)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Kolom kanan: tanggal + hapus
        rightCol = QWidget()
        rightColLayout = QVBoxLayout(rightCol)
        rightColLayout.setSpacing(8)
        rightColLayout.setContentsMargins(0, 0, 0, 0)

        dateAdded1 = QLabel("Ditambahkan pada 15 Maret 2026")
        dateAdded1.setAlignment(Qt.AlignRight)
        dateAdded1.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 12px; font-family: Arial; }}
        """)
        rightColLayout.addWidget(dateAdded1)

        rightColLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btnDelete1 = QPushButton("🗑")
        btnDelete1.setFixedSize(QSize(36, 36))
        btnDelete1.setCursor(QCursor(Qt.PointingHandCursor))
        btnDelete1.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(231, 76, 60, 0.1); color: #e74c3c;
                border: 1px solid rgba(231, 76, 60, 0.4); border-radius: 6px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #e74c3c; color: {TEXT1}; }}
        """)
        rightColLayout.addWidget(btnDelete1, alignment=Qt.AlignRight)

        layout.addWidget(rightCol)
        return card

    def _build_game_card_2(self):
        """Card: Hollow Knight"""
        card = QWidget()
        card.setObjectName("card2")
        card.setStyleSheet(f"""
            QWidget#card2 {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QWidget#card2:hover {{ border: 1px solid {ACCENT_HOVER}; }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Thumbnail
        thumb = QLabel("[ Hollow Knight ]")
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setFixedSize(QSize(170, 90))
        thumb.setStyleSheet(f"""
            QLabel {{
                background-color: {TAG_BG}; color: {TEXT2}; font-size: 11px;
                font-family: Arial; border-radius: 4px;
            }}
        """)
        layout.addWidget(thumb)

        # Info game
        infoWidget = QWidget()
        infoLayout = QVBoxLayout(infoWidget)
        infoLayout.setSpacing(6)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        nameLabel = QLabel("Hollow Knight")
        nameLabel.setStyleSheet(f"""
            QLabel {{ color: {TEXT1}; font-size: 17px; font-weight: bold; font-family: Arial; }}
        """)
        infoLayout.addWidget(nameLabel)

        # Tags
        tagsWidget = QWidget()
        tagsLayout = QHBoxLayout(tagsWidget)
        tagsLayout.setSpacing(6)
        tagsLayout.setContentsMargins(0, 0, 0, 0)
        tag_style = f"""
            QLabel {{
                background-color: {TAG_BG}; color: {TEXT2}; font-size: 11px;
                font-family: Arial; border-radius: 4px; padding: 2px 8px;
                border: 1px solid {BORDER};
            }}
        """
        for tag_text in ["Platform", "Indie", "Adventure"]:
            t = QLabel(tag_text)
            t.setStyleSheet(tag_style)
            tagsLayout.addWidget(t)
        tagsLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        infoLayout.addWidget(tagsWidget)

        # Harga
        priceRow = QWidget()
        priceLayout = QHBoxLayout(priceRow)
        priceLayout.setSpacing(8)
        priceLayout.setContentsMargins(0, 0, 0, 0)

        rating2 = QLabel("95")
        rating2.setFixedSize(QSize(44, 44))
        rating2.setAlignment(Qt.AlignCenter)
        rating2.setStyleSheet(f"""
            QLabel {{
                background-color: transparent; color: {ACCENT}; font-size: 12px;
                font-weight: bold; font-family: Arial; border: 3px solid {ACCENT}; border-radius: 22px;
            }}
        """)
        priceLayout.addWidget(rating2)

        discount2 = QLabel("-40%")
        discount2.setStyleSheet(f"""
            QLabel {{
                background-color: {ACCENT}; color: #000000; font-size: 12px;
                font-weight: bold; font-family: Arial; border-radius: 4px; padding: 2px 6px;
            }}
        """)
        priceLayout.addWidget(discount2)

        origPrice2 = QLabel("Rp 149.999")
        origPrice2.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 12px; font-family: Arial; text-decoration: line-through; }}
        """)
        priceLayout.addWidget(origPrice2)

        salePrice2 = QLabel("Rp 89.999")
        salePrice2.setStyleSheet(f"""
            QLabel {{ color: {ACCENT}; font-size: 15px; font-weight: bold; font-family: Arial; }}
        """)
        priceLayout.addWidget(salePrice2)
        priceLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        infoLayout.addWidget(priceRow)
        layout.addWidget(infoWidget)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Kolom kanan: tanggal + hapus
        rightCol = QWidget()
        rightColLayout = QVBoxLayout(rightCol)
        rightColLayout.setSpacing(8)
        rightColLayout.setContentsMargins(0, 0, 0, 0)

        dateAdded2 = QLabel("Ditambahkan pada 1 April 2026")
        dateAdded2.setAlignment(Qt.AlignRight)
        dateAdded2.setStyleSheet(f"""
            QLabel {{ color: {TEXT2}; font-size: 12px; font-family: Arial; }}
        """)
        rightColLayout.addWidget(dateAdded2)

        rightColLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btnDelete2 = QPushButton("🗑")
        btnDelete2.setFixedSize(QSize(36, 36))
        btnDelete2.setCursor(QCursor(Qt.PointingHandCursor))
        btnDelete2.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(231, 76, 60, 0.1); color: #e74c3c;
                border: 1px solid rgba(231, 76, 60, 0.4); border-radius: 6px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #e74c3c; color: {TEXT1}; }}
        """)
        rightColLayout.addWidget(btnDelete2, alignment=Qt.AlignRight)

        layout.addWidget(rightCol)
        return card

    def _build_cta_card(self):
        """Card CTA: Tambah Game"""
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

    # ===== PAGE 1: Wishlist Kosong =====
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