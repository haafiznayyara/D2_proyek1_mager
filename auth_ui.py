"""
MAGER - Auth UI (Login & Register)
Halaman login dan register dengan desain dark sesuai screenshot.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush,
    QLinearGradient, QPalette, QCursor
)

# ── Palette (sama dengan dashboard) ──────────────────────────────────────────
BG        = "#0d1117"
BG_CARD   = "#161b27"
BG_INPUT  = "#1e2535"
BORDER    = "#2a3555"
BORDER_F  = "#00e676"   # focus
WHITE     = "#ffffff"
LIGHT     = "#c9d1e0"
MUTED     = "#7b8db0"
GREEN     = "#00e676"
GREEN_HOV = "#00c853"
LINK      = "#00bcd4"


def _field_qss(focused_color=BORDER_F):
    return f"""
        QLineEdit {{
            background: {BG_INPUT};
            border: 1px solid {BORDER};
            border-radius: 8px;
            color: {WHITE};
            font-size: 13px;
            padding: 0 14px 0 38px;
        }}
        QLineEdit:focus {{
            border: 1px solid {focused_color};
        }}
        QLineEdit::placeholder {{
            color: {MUTED};
        }}
    """


# ── Icon Label (prefix di dalam field) ───────────────────────────────────────
class _IconField(QWidget):
    def __init__(self, placeholder: str, icon: str, echo=QLineEdit.Normal, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._container = QWidget()
        self._container.setStyleSheet(f"""
            QWidget {{
                background: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        self._container.setFixedHeight(44)
        cl = QHBoxLayout(self._container)
        cl.setContentsMargins(12, 0, 12, 0)
        cl.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(18, 18)
        icon_lbl.setStyleSheet(
            f"color: {MUTED}; font-size: 14px; background: transparent; border: none;"
        )
        icon_lbl.setAlignment(Qt.AlignCenter)

        # Subclass QLineEdit agar override event aman
        outer = self
        class _Field(QLineEdit):
            def focusInEvent(self, e):
                outer._set_border(GREEN)
                super().focusInEvent(e)
            def focusOutEvent(self, e):
                outer._set_border(BORDER)
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
                font-family: 'Segoe UI';
            }}
        """)

        cl.addWidget(icon_lbl)
        cl.addWidget(self.field)
        lay.addWidget(self._container)

    def _set_border(self, color: str):
        self._container.setStyleSheet(f"""
            QWidget {{
                background: {BG_INPUT};
                border: 1px solid {color};
                border-radius: 8px;
            }}
        """)

    def text(self) -> str:
        return self.field.text()

    def clear(self):
        self.field.clear()

    def setFocus(self):
        self.field.setFocus()

    def _set_border(self, color: str):
        self._container.setStyleSheet(f"""
            QWidget {{
                background: {BG_INPUT};
                border: 1px solid {color};
                border-radius: 8px;
            }}
        """)

    def text(self) -> str:
        return self.field.text()

    def clear(self):
        self.field.clear()

    def setFocus(self):
        self.field.setFocus()


# ── Card base ─────────────────────────────────────────────────────────────────
class _AuthCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)


# ── LoginWindow ───────────────────────────────────────────────────────────────
class LoginWindow(QWidget):
    login_success   = pyqtSignal(object)   # emit user dict saat login berhasil
    go_register     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = _AuthCard()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 32, 28, 28)
        cl.setSpacing(0)

        # Judul
        title = QLabel("Selamat Datang")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {WHITE}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(4)

        sub = QLabel("Login untuk melanjutkan")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        cl.addSpacing(24)

        # Username
        lbl_u = QLabel("Username")
        lbl_u.setFont(QFont("Segoe UI", 10))
        lbl_u.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
        cl.addWidget(lbl_u)
        cl.addSpacing(6)

        self.inp_user = _IconField("Masukkan username", "👤")
        cl.addWidget(self.inp_user)

        cl.addSpacing(14)

        # Password
        lbl_p = QLabel("Password")
        lbl_p.setFont(QFont("Segoe UI", 10))
        lbl_p.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
        cl.addWidget(lbl_p)
        cl.addSpacing(6)

        self.inp_pass = _IconField("Masukkan password", "🔒", QLineEdit.Password)
        cl.addWidget(self.inp_pass)

        cl.addSpacing(6)

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setFont(QFont("Segoe UI", 9))
        self.lbl_error.setStyleSheet(f"color: #ef4444; background: transparent; border: none;")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        cl.addWidget(self.lbl_error)

        cl.addSpacing(16)

        # Tombol Login
        self.btn_login = QPushButton("Login")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN};
                border: none;
                border-radius: 8px;
                color: #0d1117;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {GREEN_HOV}; }}
            QPushButton:pressed {{ background: #009624; }}
        """)
        self.btn_login.clicked.connect(self._do_login)
        cl.addWidget(self.btn_login)

        cl.addSpacing(14)

        # Link register
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
            QPushButton {{
                background: transparent;
                border: none;
                color: {LINK};
                padding: 0;
            }}
            QPushButton:hover {{ color: {GREEN}; }}
        """)
        btn_reg.clicked.connect(self.go_register)
        link_row.addWidget(lbl_q)
        link_row.addWidget(btn_reg)
        cl.addLayout(link_row)

        root.addWidget(card, alignment=Qt.AlignCenter)

    def _do_login(self):
        from auth_logic import login_user
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()

        if not username or not password:
            self.lbl_error.setText("Username dan password tidak boleh kosong.")
            return

        result = login_user(username, password)
        if result["success"]:
            self.lbl_error.setText("")
            self.inp_user.clear()
            self.inp_pass.clear()
            self.login_success.emit(result["user"])
        else:
            self.lbl_error.setText(result["message"])

    def show_error(self, msg: str):
        self.lbl_error.setText(msg)


# ── RegisterWindow ────────────────────────────────────────────────────────────
class RegisterWindow(QWidget):
    register_success = pyqtSignal()
    go_login         = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background: {BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = _AuthCard()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 32, 28, 28)
        cl.setSpacing(0)

        # Judul
        title = QLabel("Daftar Akun Baru")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {WHITE}; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        cl.addSpacing(4)

        sub = QLabel("Buat akun untuk mulai menggunakan MAGER")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {MUTED}; background: transparent; border: none;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        cl.addWidget(sub)

        cl.addSpacing(24)

        # Username
        lbl_u = QLabel("Username")
        lbl_u.setFont(QFont("Segoe UI", 10))
        lbl_u.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
        cl.addWidget(lbl_u)
        cl.addSpacing(6)
        self.inp_user = _IconField("Masukkan username", "👤")
        cl.addWidget(self.inp_user)

        cl.addSpacing(14)

        # Password
        lbl_p = QLabel("Password")
        lbl_p.setFont(QFont("Segoe UI", 10))
        lbl_p.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
        cl.addWidget(lbl_p)
        cl.addSpacing(6)
        self.inp_pass = _IconField("Masukkan password", "🔒", QLineEdit.Password)
        cl.addWidget(self.inp_pass)

        cl.addSpacing(14)

        # Konfirmasi Password
        lbl_c = QLabel("Konfirmasi Password")
        lbl_c.setFont(QFont("Segoe UI", 10))
        lbl_c.setStyleSheet(f"color: {LIGHT}; background: transparent; border: none;")
        cl.addWidget(lbl_c)
        cl.addSpacing(6)
        self.inp_confirm = _IconField("Konfirmasi password", "🔒", QLineEdit.Password)
        cl.addWidget(self.inp_confirm)

        cl.addSpacing(6)

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setFont(QFont("Segoe UI", 9))
        self.lbl_error.setStyleSheet(f"color: #ef4444; background: transparent; border: none;")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        cl.addWidget(self.lbl_error)

        cl.addSpacing(16)

        # Tombol Daftar
        self.btn_reg = QPushButton("Daftar")
        self.btn_reg.setFixedHeight(42)
        self.btn_reg.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_reg.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_reg.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN};
                border: none;
                border-radius: 8px;
                color: #0d1117;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {GREEN_HOV}; }}
            QPushButton:pressed {{ background: #009624; }}
        """)
        self.btn_reg.clicked.connect(self._do_register)
        cl.addWidget(self.btn_reg)

        cl.addSpacing(14)

        # Link login
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
            QPushButton {{
                background: transparent;
                border: none;
                color: {LINK};
                padding: 0;
            }}
            QPushButton:hover {{ color: {GREEN}; }}
        """)
        btn_login.clicked.connect(self.go_login)
        link_row.addWidget(lbl_q)
        link_row.addWidget(btn_login)
        cl.addLayout(link_row)

        root.addWidget(card, alignment=Qt.AlignCenter)

    def _do_register(self):
        from auth_logic import register_user
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()
        confirm  = self.inp_confirm.text()

        if not username or not password or not confirm:
            self.lbl_error.setText("Semua field harus diisi.")
            return
        if password != confirm:
            self.lbl_error.setText("Password dan konfirmasi tidak cocok.")
            return
        if len(password) < 6:
            self.lbl_error.setText("Password minimal 6 karakter.")
            return

        result = register_user(username, password)
        if result["success"]:
            self.lbl_error.setText("")
            self.inp_user.clear()
            self.inp_pass.clear()
            self.inp_confirm.clear()
            self.register_success.emit()
        else:
            self.lbl_error.setText(result["message"])