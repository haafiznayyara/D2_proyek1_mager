"""
MAGER - Auth UI (Login & Register)
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSizePolicy, QFrame,

)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap, QCursor

def _asset(name):
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", name)

BG           = "#0A1123"
BG_CARD      = "#1A1F36"
BG_INPUT     = "#2A3050"
BORDER       = "#2A3050"
BORDER_F     = "#4ADE80"
WHITE        = "#FFFFFF"
LIGHT        = "#D1D5DC"
MUTED        = "#99A1AF"
GREEN        = "#4ADE80"
BLACK        = "#000000"
ERROR_BG     = "rgba(147,40,40,0.6)"
ERROR_BORDER = "#E81B1B"
ERROR_TEXT   = "#F26969"

CARD_W  = 400
CARD_W_SUCCESS = 460
FIELD_H = 42
BTN_H   = 44


class _IconField(QWidget):
    def __init__(self, placeholder, icon_path, echo=QLineEdit.Normal, parent=None):
        super().__init__(parent)
        self.setFixedHeight(FIELD_H)
        self._has_error = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._container = QFrame()
        self._container.setFixedHeight(FIELD_H)
        self._apply_style(BORDER)

        cl = QHBoxLayout(self._container)
        cl.setContentsMargins(12, 0, 12, 0)
        cl.setSpacing(8)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(16, 16)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setStyleSheet("background: transparent; border: none;")
        pix = QPixmap(icon_path)
        if not pix.isNull():
            self._icon_lbl.setPixmap(
                pix.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        outer = self

        class _Field(QLineEdit):
            def focusInEvent(self, e):
                if not outer._has_error:
                    outer._apply_style(BORDER_F)
                super().focusInEvent(e)
            def focusOutEvent(self, e):
                if not outer._has_error:
                    outer._apply_style(BORDER)
                super().focusOutEvent(e)

        self.field = _Field()
        self.field.setPlaceholderText(placeholder)
        self.field.setEchoMode(echo)
        self.field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {WHITE};
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLineEdit::placeholder {{ color: {MUTED}; }}
        """)

        cl.addWidget(self._icon_lbl)
        cl.addWidget(self.field)
        lay.addWidget(self._container)

    def _apply_style(self, color):
        self._container.setStyleSheet(f"""
            QFrame {{
                background: {BG_INPUT};
                border: 1px solid {color};
                border-radius: 10px;
            }}
        """)

    def set_error(self, has_error):
        self._has_error = has_error
        self._apply_style(ERROR_BORDER if has_error else BORDER)

    def text(self):     return self.field.text()
    def clear(self):    self.field.clear(); self.set_error(False)
    def setFocus(self): self.field.setFocus()


class SuccessRegisterPage(QWidget):
    """Halaman penuh success register — menggantikan popup."""
    go_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 16px;
                border: none;
            }}
        """)
        card.setFixedWidth(CARD_W_SUCCESS)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 48, 28, 60)
        cl.setSpacing(0)
        cl.setAlignment(Qt.AlignCenter)

        icon_circle = QLabel()
        icon_circle.setFixedSize(72, 72)
        icon_circle.setAlignment(Qt.AlignCenter)
        icon_circle.setStyleSheet(f"""
            QLabel {{
                background: {GREEN};
                border-radius: 36px;
                border: none;
            }}
        """)
        pix = QPixmap(_asset("tick_filled.png"))
        if not pix.isNull():
            icon_circle.setPixmap(
                pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        cl.addWidget(icon_circle, alignment=Qt.AlignCenter)

        cl.addSpacing(20)

        title = QLabel("Pendaftaran Berhasil!")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {WHITE}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        cl.addWidget(title)

        cl.addSpacing(8)

        sub = QLabel("Anda akan dipindahkan ke halaman login . .")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(False)
        cl.addWidget(sub)

        root.addStretch()
        root.addWidget(card, alignment=Qt.AlignCenter)
        root.addStretch()

    def show_and_redirect(self):
        """Panggil setiap kali halaman ini ditampilkan."""
        QTimer.singleShot(2500, self.go_login.emit)


def _field_block(parent_layout, label_text, field_widget, spacing_before=10):
    """Helper: tambah label + field ke layout."""
    parent_layout.addSpacing(spacing_before)
    lbl = QLabel(label_text)
    lbl.setFont(QFont("Segoe UI", 9))
    lbl.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
    parent_layout.addWidget(lbl)
    parent_layout.addSpacing(4)
    parent_layout.addWidget(field_widget)


class LoginWindow(QWidget):
    login_success = pyqtSignal(object)
    go_register   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 16px;
                border: none;
            }}
        """)
        card.setFixedWidth(CARD_W)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(0)

        # Title
        title = QLabel("Selamat Datang")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {WHITE}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        cl.addWidget(title)

        cl.addSpacing(4)

        sub = QLabel("Login untuk melanjutkan")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Fields
        self.inp_user = _IconField("Masukkan username", _asset("avatar_outline.png"))
        self.inp_pass = _IconField("Masukkan password", _asset("lock_outline.png"), QLineEdit.Password)
        _field_block(cl, "Username", self.inp_user, spacing_before=16)
        _field_block(cl, "Password", self.inp_pass, spacing_before=10)

        # Error box
        cl.addSpacing(8)
        self._err_frame = QFrame()
        self._err_frame.setStyleSheet(f"""
            QFrame {{
                background: {ERROR_BG};
                border: 1px solid {ERROR_BORDER};
                border-radius: 8px;
            }}
        """)
        self._err_frame.setVisible(False)
        err_lay = QHBoxLayout(self._err_frame)
        err_lay.setContentsMargins(12, 7, 12, 7)
        self.lbl_error = QLabel("")
        self.lbl_error.setFont(QFont("Segoe UI", 9))
        self.lbl_error.setStyleSheet(f"color: {ERROR_TEXT}; background: transparent; border: none;")
        self.lbl_error.setWordWrap(True)
        err_lay.addWidget(self.lbl_error)
        cl.addWidget(self._err_frame)

        # Button
        cl.addSpacing(12)
        self.btn_login = QPushButton("Login")
        self.btn_login.setFixedHeight(BTN_H)
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN}; border: none;
                border-radius: 10px; color: {BLACK}; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3dcc70; }}
            QPushButton:pressed {{ background: #2ebd60; }}
        """)
        self.btn_login.clicked.connect(self._do_login)
        cl.addWidget(self.btn_login)

        # Link
        cl.addSpacing(12)
        link_row = QHBoxLayout()
        link_row.setAlignment(Qt.AlignCenter)
        link_row.setSpacing(4)
        lbl_q = QLabel("Belum punya akun?")
        lbl_q.setFont(QFont("Segoe UI", 9))
        lbl_q.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        btn_reg = QPushButton("Daftar sekarang")
        btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        btn_reg.setFont(QFont("Segoe UI", 9))
        btn_reg.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; color: {GREEN}; padding: 0; }}
            QPushButton:hover {{ color: #3dcc70; }}
        """)
        btn_reg.clicked.connect(self.go_register)
        link_row.addWidget(lbl_q)
        link_row.addWidget(btn_reg)
        cl.addLayout(link_row)

        root.addStretch()
        root.addWidget(card, alignment=Qt.AlignCenter)
        root.addStretch()

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self._err_frame.setVisible(bool(msg))

    def _do_login(self):
        from auth_logic import login_user
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()
        if not username or not password:
            self._show_error("Username dan password tidak boleh kosong.")
            return
        result = login_user(username, password)
        if result["success"]:
            self._show_error("")
            self.inp_user.clear()
            self.inp_pass.clear()
            self.login_success.emit(result["user"])
        else:
            self._show_error(result["message"])

    def show_error(self, msg):
        self._show_error(msg)


class RegisterWindow(QWidget):
    register_success = pyqtSignal()
    go_login         = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 16px;
                border: none;
            }}
        """)
        card.setFixedWidth(CARD_W)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(0)

        # Title
        title = QLabel("Daftar Akun Baru")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {WHITE}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        cl.addWidget(title)

        cl.addSpacing(4)

        sub = QLabel("Buat akun untuk mulai menggunakan MAGER")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # Fields
        self.inp_user    = _IconField("Masukkan username",   _asset("avatar_outline.png"))
        self.inp_pass    = _IconField("Masukkan password",   _asset("lock_outline.png"), QLineEdit.Password)
        self.inp_confirm = _IconField("Konfirmasi password", _asset("lock_outline.png"), QLineEdit.Password)
        _field_block(cl, "Username",            self.inp_user,    spacing_before=16)
        _field_block(cl, "Password",            self.inp_pass,    spacing_before=10)
        _field_block(cl, "Konfirmasi Password", self.inp_confirm, spacing_before=10)

        # Error box
        cl.addSpacing(8)
        self._err_frame = QFrame()
        self._err_frame.setStyleSheet(f"""
            QFrame {{
                background: {ERROR_BG};
                border: 1px solid {ERROR_BORDER};
                border-radius: 8px;
            }}
        """)
        self._err_frame.setVisible(False)
        err_lay = QHBoxLayout(self._err_frame)
        err_lay.setContentsMargins(12, 7, 12, 7)
        self.lbl_error = QLabel("")
        self.lbl_error.setFont(QFont("Segoe UI", 9))
        self.lbl_error.setStyleSheet(f"color: {ERROR_TEXT}; background: transparent; border: none;")
        self.lbl_error.setWordWrap(True)
        err_lay.addWidget(self.lbl_error)
        cl.addWidget(self._err_frame)

        # Button
        cl.addSpacing(12)
        self.btn_reg = QPushButton("Daftar")
        self.btn_reg.setFixedHeight(BTN_H)
        self.btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_reg.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_reg.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN}; border: none;
                border-radius: 10px; color: {BLACK}; font-weight: bold;
            }}
            QPushButton:hover {{ background: #3dcc70; }}
            QPushButton:pressed {{ background: #2ebd60; }}
        """)
        self.btn_reg.clicked.connect(self._do_register)
        cl.addWidget(self.btn_reg)

        # Link
        cl.addSpacing(12)
        link_row = QHBoxLayout()
        link_row.setAlignment(Qt.AlignCenter)
        link_row.setSpacing(4)
        lbl_q = QLabel("Sudah punya akun?")
        lbl_q.setFont(QFont("Segoe UI", 9))
        lbl_q.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        btn_login = QPushButton("Login sekarang")
        btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        btn_login.setFont(QFont("Segoe UI", 9))
        btn_login.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; color: {GREEN}; padding: 0; }}
            QPushButton:hover {{ color: #3dcc70; }}
        """)
        btn_login.clicked.connect(self.go_login)
        link_row.addWidget(lbl_q)
        link_row.addWidget(btn_login)
        cl.addLayout(link_row)

        root.addStretch()
        root.addWidget(card, alignment=Qt.AlignCenter)
        root.addStretch()

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self._err_frame.setVisible(bool(msg))

    def _do_register(self):
        from auth_logic import register_user
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()
        confirm  = self.inp_confirm.text()
        if not username or not password or not confirm:
            self._show_error("Semua bagian harus diisi.")
            return
        if password != confirm:
            self._show_error("Password dan konfirmasi password tidak cocok.")
            return
        if len(password) < 6:
            self._show_error("Password minimal 6 karakter.")
            return
        result = register_user(username, password)
        if result["success"]:
            self._show_error("")
            self.inp_user.clear()
            self.inp_pass.clear()
            self.inp_confirm.clear()
            self._show_success_popup()
        else:
            self._show_error(result["message"])

    def _show_success_popup(self):
        self.register_success.emit()