# navbar.py
import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon, QBrush, QPen

_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ── Warna ─────────────────────────────────────────────────────────────────
_WHITE  = "#FFFFFF"
_MUTED  = "#99A1AF"
_DARK   = "#515050"
_BLACK  = "#000000"
_GREEN  = "#4ADE80"


def _tint_pixmap(path: str, color: str, size: int = 20) -> QPixmap:
    raw = QPixmap(path)
    if raw.isNull():
        return QPixmap()
    raw = raw.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    result = QPixmap(raw.size())
    result.fill(Qt.transparent)
    p = QPainter(result)
    p.drawPixmap(0, 0, raw)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(result.rect(), QColor(color))
    p.end()
    return result


# ── SearchBox — pakai paintEvent supaya border 100% dikontrol sendiri ─────
class SearchBox(QWidget):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._focused = False
        self.setFixedHeight(40)
        self.setMinimumWidth(260)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(0)

        # Input
        self._edit = QLineEdit()
        self._edit.setFrame(False)
        self._edit.setFont(QFont("Segoe UI", 11))
        self._edit.setStyleSheet(
            f"background:transparent; border:none; color:{_WHITE};"
            f"selection-background-color:{_GREEN}; selection-color:{_BLACK};"
        )
        lay.addWidget(self._edit, stretch=1)

        # Icon kanan
        self._icon = QLabel()
        self._icon.setFixedSize(18, 18)
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setStyleSheet("background:transparent; border:none;")
        _sp = os.path.join(_HERE, "search_outline.png")
        if os.path.exists(_sp):
            self._icon.setPixmap(_tint_pixmap(_sp, _MUTED, 16))
        lay.addWidget(self._icon)

        # Placeholder overlay
        self._ph = QLabel("Search games...", self)
        self._ph.setFont(QFont("Segoe UI", 11))
        self._ph.setStyleSheet(f"color:{_MUTED}; background:transparent; border:none;")
        self._ph.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._ph.raise_()

        self._edit.textChanged.connect(self._on_text)
        self._edit.focusInEvent  = self._on_focus_in
        self._edit.focusOutEvent = self._on_focus_out

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.75, 0.75, -0.75, -0.75)
        p.setBrush(QBrush(QColor(_DARK)))
        if self._focused:
            p.setPen(QPen(QColor(_GREEN), 1.5))
        else:
            p.setPen(Qt.NoPen)
        p.drawRoundedRect(rect, 8, 8)
        p.end()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._ph.setGeometry(12, 0, self.width() - 40, self.height())

    def _on_text(self, text):
        has = bool(text)
        self._ph.setVisible(not has)
        self._icon.setVisible(not has)
        self.textChanged.emit(text)

    def _on_focus_in(self, ev):
        self._focused = True
        self.update()
        QLineEdit.focusInEvent(self._edit, ev)

    def _on_focus_out(self, ev):
        self._focused = False
        self.update()
        QLineEdit.focusOutEvent(self._edit, ev)

    def text(self):
        return self._edit.text()

    def clear(self):
        self._edit.clear()


# ── Navbar ────────────────────────────────────────────────────────────────
class Navbar(QWidget):
    search_changed    = pyqtSignal(str)
    dashboard_clicked = pyqtSignal()
    popular_clicked   = pyqtSignal()
    cheapest_clicked  = pyqtSignal()
    wishlist_clicked  = pyqtSignal()
    profile_clicked   = pyqtSignal()

    def __init__(self, active_page: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background:{_BLACK};")

        h = QHBoxLayout(self)
        h.setContentsMargins(28, 0, 28, 0)
        h.setSpacing(0)

        # Logo — klik untuk balik ke dashboard, warna tetap putih
        logo = QPushButton("MAGER")
        logo.setFont(QFont("Consolas", 18, QFont.Bold))
        logo.setCursor(QCursor(Qt.PointingHandCursor))
        logo.setStyleSheet(f"""
            QPushButton {{
                color: {_WHITE};
                letter-spacing: 4px;
                background: transparent;
                border: none;
                padding: 0;
            }}
            QPushButton:hover {{ color: {_WHITE}; }}
            QPushButton:pressed {{ color: {_WHITE}; }}
        """)
        logo.clicked.connect(self.dashboard_clicked)
        h.addWidget(logo)
        h.addSpacing(36)

        # Nav links
        for label, page_key, sig in [
            ("Game Populer", "popular",  self.popular_clicked),
            ("Filter Harga", "cheapest", self.cheapest_clicked),
        ]:
            is_active = active_page == page_key
            color = _GREEN if is_active else _MUTED
            btn = QPushButton(label)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {color}; font-family: 'Segoe UI';
                    font-size: 13px; padding: 0 16px;
                    {'font-weight:bold;' if is_active else ''}
                }}
                QPushButton:hover {{ color:{_WHITE}; }}
            """)
            btn.clicked.connect(sig)
            h.addWidget(btn)

        h.addStretch()

        # Search
        self.search_box = SearchBox()
        self.search_box.textChanged.connect(self.search_changed)
        h.addWidget(self.search_box)
        h.addSpacing(10)

        # Icon button helper
        def _icon_btn(png_name, fallback, page_key, tooltip, signal):
            active     = active_page == page_key
            icon_color = _GREEN if active else _WHITE
            b = QPushButton()
            b.setFixedSize(42, 40)
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setToolTip(tooltip)
            border_line = f"1.5px solid {_GREEN}" if active else "none"
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {_DARK}; border: {border_line}; border-radius: 8px;
                }}
                QPushButton:hover {{ background:{_MUTED}; }}
                QPushButton:pressed {{ background:{_GREEN}; }}
            """)
            path = os.path.join(_HERE, png_name)
            if os.path.exists(path):
                b.setIcon(QIcon(_tint_pixmap(path, icon_color, 20)))
                b.setIconSize(QSize(20, 20))
            else:
                b.setText(fallback)
                b.setStyleSheet(b.styleSheet() + f"color:{icon_color}; font-size:16px;")
            b.clicked.connect(signal)
            return b

        self.wishlist_btn = _icon_btn(
            "wishlist_outline.png", "♡", "wishlist", "Wishlist", self.wishlist_clicked
        )
        h.addWidget(self.wishlist_btn)
        h.addSpacing(8)

        self.profile_btn = _icon_btn(
            "avatar_outline_white.png", "👤", "profile", "Akun Saya", self.profile_clicked
        )
        h.addWidget(self.profile_btn)