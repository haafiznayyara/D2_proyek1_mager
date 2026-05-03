"""
MAGER - Halaman Profil Pengguna
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QRect, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush,
    QLinearGradient, QCursor, QRadialGradient, QPixmap
)
from widget.navbar import Navbar

# Palette
BG      = "#0d1117"
BG_DARK = "#161b27"
BG_CARD = "#1a2035"
BG_ELEM = "#1e2840"
BORDER  = "#2a3555"
WHITE   = "#ffffff"
LIGHT   = "#c9d1e0"
MUTED   = "#7b8db0"
GREEN   = "#00c853"
ACCENT  = "#58a6ff"
GOLD    = "#ffc107"
RED     = "#e05252"


# ── Avatar Widget ─────────────────────────────────────────────────────────────
class AvatarWidget(QWidget):
    def __init__(self, initials="MG", color="#58a6ff", size=90, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.color    = color
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.width() // 2

        grad = QRadialGradient(r, r, r)
        grad.setColorAt(0, QColor(self.color).lighter(140))
        grad.setColorAt(1, QColor(self.color).darker(160))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())

        p.setPen(QColor(WHITE))
        p.setFont(QFont("Segoe UI", r // 2, QFont.Bold))
        p.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, self.initials)


# ── Stat Card ─────────────────────────────────────────────────────────────────
def stat_card(icon, label, value, color=ACCENT):
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}
    """)
    v = QVBoxLayout(f)
    v.setContentsMargins(16, 14, 16, 14)
    v.setSpacing(4)

    ico = QLabel(icon)
    ico.setFont(QFont("Segoe UI", 22))
    ico.setStyleSheet("background:transparent;")
    v.addWidget(ico)

    val = QLabel(str(value))
    val.setFont(QFont("Segoe UI", 18, QFont.Bold))
    val.setStyleSheet(f"color:{color};background:transparent;")
    v.addWidget(val)

    lbl = QLabel(label)
    lbl.setFont(QFont("Segoe UI", 10))
    lbl.setStyleSheet(f"color:{MUTED};background:transparent;")
    v.addWidget(lbl)

    return f


# ── Activity Row ──────────────────────────────────────────────────────────────
def activity_row(title, genre, time_ago, ac="#58a6ff"):
    row = QWidget()
    row.setStyleSheet(f"background:{BG_ELEM};border-radius:8px;")
    h = QHBoxLayout(row)
    h.setContentsMargins(14, 10, 14, 10)
    h.setSpacing(12)

    dot = QLabel()
    dot.setFixedSize(10, 10)
    dot.setStyleSheet(f"background:{ac};border-radius:5px;")
    h.addWidget(dot, alignment=Qt.AlignVCenter)

    info = QVBoxLayout(); info.setSpacing(2)
    t = QLabel(title)
    t.setFont(QFont("Segoe UI", 11, QFont.Bold))
    t.setStyleSheet(f"color:{WHITE};background:transparent;")
    g = QLabel(genre)
    g.setFont(QFont("Segoe UI", 9))
    g.setStyleSheet(f"color:{MUTED};background:transparent;")
    info.addWidget(t); info.addWidget(g)
    h.addLayout(info, stretch=1)

    tm = QLabel(time_ago)
    tm.setFont(QFont("Segoe UI", 9))
    tm.setStyleSheet(f"color:{MUTED};background:transparent;")
    h.addWidget(tm)
    return row


class ProfileWindow(QWidget):
    back_clicked     = pyqtSignal()
    wishlist_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav = Navbar(active_page="profile")
        self.nav.wishlist_clicked.connect(self.wishlist_clicked)
        # self.nav.profile_clicked.connect(...)  # atau biarkan jika tidak diperlukan
        root.addWidget(self.nav)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background:{BG}; border:none; }}
            QScrollBar:vertical {{ background:{BG_CARD}; width:6px; border-radius:3px; }}
            QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:20px; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
        """)

        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 16, 28, 28)
        cl.setSpacing(20)

        # Back button
        back_row = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setCursor(QCursor(Qt.PointingHandCursor))
        btn_back.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;color:{MUTED};"
            f"font-size:13px;}} QPushButton:hover{{color:{WHITE};}}"
        )
        btn_back.clicked.connect(self.back_clicked)
        back_row.addWidget(btn_back)
        back_row.addStretch()
        cl.addLayout(back_row)

        # Profile header card
        cl.addWidget(self._profile_header())

        # Stats grid
        cl.addWidget(self._stats_section())

        # Aktivitas & badge
        two_col = QHBoxLayout(); two_col.setSpacing(16)
        two_col.addWidget(self._activity_section(), stretch=3)
        two_col.addWidget(self._badges_section(), stretch=2)
        cl.addLayout(two_col)

        # Pengaturan akun
        cl.addWidget(self._settings_section())

        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── Navbar ────────────────────────────────────────────────────────────
    def _navbar(self):
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"background:{BG_DARK};border-bottom:1px solid {BORDER};")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(0)

        logo = QLabel("MAGER")
        logo.setStyleSheet(f"color:{WHITE};font-size:20px;font-weight:900;letter-spacing:1px;")
        h.addWidget(logo)
        h.addSpacing(24)

        for txt in ["Popular Games", "Cheapest Games"]:
            btn = QPushButton(txt)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(
                f"QPushButton{{background:transparent;border:none;color:{MUTED};"
                f"font-size:13px;padding:8px 14px;}} QPushButton:hover{{color:{WHITE};}}"
            )
            h.addWidget(btn)

        h.addStretch()

        search = QLineEdit()
        search.setPlaceholderText("Search games...")
        search.setFixedSize(200, 32)
        search.setStyleSheet(
            f"QLineEdit{{background:{BG_ELEM};border:1px solid {BORDER};"
            f"border-radius:16px;padding:0 14px;color:{WHITE};font-size:12px;}}"
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
        heart.clicked.connect(self.wishlist_clicked)
        h.addWidget(heart)
        h.addSpacing(8)

        user = QPushButton("👤")
        user.setFixedSize(34, 34)
        user.setStyleSheet(
            f"QPushButton{{background:{BG_ELEM};border:1px solid {ACCENT};"
            f"border-radius:17px;color:{ACCENT};font-size:14px;}}"
        )
        h.addWidget(user)
        return bar

    # ── Profile Header ────────────────────────────────────────────────────
    def _profile_header(self):
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1a2035, stop:1 #0d1117);
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        h = QHBoxLayout(f)
        h.setContentsMargins(24, 20, 24, 20)
        h.setSpacing(20)

        avatar = AvatarWidget("AG", ACCENT, 80)
        h.addWidget(avatar)

        info = QVBoxLayout(); info.setSpacing(4)
        name = QLabel("Ahmad Gamer")
        name.setFont(QFont("Segoe UI", 18, QFont.Bold))
        name.setStyleSheet(f"color:{WHITE};background:transparent;")
        info.addWidget(name)

        username = QLabel("@ahmadgamer · Bergabung Jan 2023")
        username.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        info.addWidget(username)

        badge_row = QHBoxLayout(); badge_row.setSpacing(6)
        for txt, col in [("🎮 Gamer Sejati", ACCENT), ("⭐ Top Reviewer", GOLD)]:
            b = QLabel(txt)
            b.setStyleSheet(
                f"background:{col}22;color:{col};font-size:10px;"
                "font-weight:bold;padding:3px 10px;border-radius:10px;"
                f"border:1px solid {col}55;"
            )
            badge_row.addWidget(b)
        badge_row.addStretch()
        info.addLayout(badge_row)
        h.addLayout(info, stretch=1)

        btn_edit = QPushButton("✏ Edit Profil")
        btn_edit.setFixedSize(120, 36)
        btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit.setStyleSheet(
            f"QPushButton{{background:transparent;border:1px solid {ACCENT};"
            f"border-radius:8px;color:{ACCENT};font-size:12px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{ACCENT};color:#000;}}"
        )
        h.addWidget(btn_edit, alignment=Qt.AlignVCenter)
        return f

    # ── Stats ─────────────────────────────────────────────────────────────
    def _stats_section(self):
        container = QWidget(); container.setStyleSheet("background:transparent;")
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)

        cards = [
            ("🎮", "Game Dimiliki",    "47",       ACCENT),
            ("♡",  "Wishlist",         "12",        "#f06292"),
            ("⭐",  "Review Ditulis",   "28",        GOLD),
            ("💰",  "Total Belanja",    "Rp 3,2 Jt", GREEN),
        ]
        for i, (icon, label, value, color) in enumerate(cards):
            grid.addWidget(stat_card(icon, label, value, color), 0, i)
        return container

    # ── Aktivitas ─────────────────────────────────────────────────────────
    def _activity_section(self):
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        title = QLabel("📋  Aktivitas Terakhir")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color:{WHITE};background:transparent;")
        v.addWidget(title)

        activities = [
            ("Cyberpunk 2077",  "RPG",          "2 jam lalu",    "#ffd700"),
            ("Elden Ring",      "Action RPG",   "1 hari lalu",   "#c0a060"),
            ("Hades",           "Roguelite",    "3 hari lalu",   "#e05252"),
            ("Hollow Knight",   "Metroidvania", "1 minggu lalu", "#7c6fa0"),
            ("Celeste",         "Platformer",   "2 minggu lalu", "#4fc3f7"),
        ]
        for args in activities:
            v.addWidget(activity_row(*args))
        return f

    # ── Badge ─────────────────────────────────────────────────────────────
    def _badges_section(self):
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        title = QLabel("🏅  Pencapaian")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color:{WHITE};background:transparent;")
        v.addWidget(title)

        badges = [
            ("🎮", "Gamer Sejati",    "Miliki 40+ game",      ACCENT),
            ("⭐",  "Top Reviewer",   "Tulis 25+ review",     GOLD),
            ("💎",  "Diamond Member", "Belanja > Rp 2 Juta",  "#b9f2ff"),
            ("🔥",  "Hot Streak",     "Login 30 hari beruntun", RED),
            ("🏆",  "Completionist",  "100% 5 game",          GREEN),
        ]

        for icon, name, desc, color in badges:
            row = QWidget()
            row.setStyleSheet(f"background:{BG_ELEM};border-radius:7px;")
            rh = QHBoxLayout(row)
            rh.setContentsMargins(12, 8, 12, 8)
            rh.setSpacing(10)

            ico = QLabel(icon)
            ico.setFont(QFont("Segoe UI", 18))
            ico.setStyleSheet("background:transparent;")
            rh.addWidget(ico)

            text = QVBoxLayout(); text.setSpacing(1)
            n = QLabel(name)
            n.setFont(QFont("Segoe UI", 10, QFont.Bold))
            n.setStyleSheet(f"color:{color};background:transparent;")
            d = QLabel(desc)
            d.setFont(QFont("Segoe UI", 8))
            d.setStyleSheet(f"color:{MUTED};background:transparent;")
            text.addWidget(n); text.addWidget(d)
            rh.addLayout(text, stretch=1)

            v.addWidget(row)

        v.addStretch()
        return f

    # ── Pengaturan Akun ───────────────────────────────────────────────────
    def _settings_section(self):
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(12)

        title = QLabel("⚙  Pengaturan Akun")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color:{WHITE};background:transparent;")
        v.addWidget(title)

        grid = QGridLayout(); grid.setSpacing(10)

        def field(label, placeholder, row, col):
            box = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(36)
            inp.setStyleSheet(
                f"QLineEdit{{background:{BG_ELEM};border:1px solid {BORDER};"
                f"border-radius:6px;padding:0 12px;color:{WHITE};font-size:12px;}}"
                f"QLineEdit:focus{{border:1px solid {ACCENT};}}"
            )
            box.addWidget(lbl); box.addWidget(inp)
            w = QWidget(); w.setStyleSheet("background:transparent;")
            QVBoxLayout(w).addLayout(box)
            # simpler: just add to grid
            container = QFrame()
            container.setStyleSheet("background:transparent;border:none;")
            cl = QVBoxLayout(container); cl.setContentsMargins(0,0,0,0); cl.setSpacing(4)
            cl.addWidget(lbl); cl.addWidget(inp)
            grid.addWidget(container, row, col)

        field("Nama Lengkap", "Ahmad Gamer", 0, 0)
        field("Username",     "@ahmadgamer", 0, 1)
        field("Email",        "ahmad@email.com", 1, 0)
        field("Kata Sandi",   "••••••••", 1, 1)
        v.addLayout(grid)

        btn_save = QPushButton("💾  Simpan Perubahan")
        btn_save.setFixedHeight(40)
        btn_save.setCursor(QCursor(Qt.PointingHandCursor))
        btn_save.setStyleSheet(
            f"QPushButton{{background:{GREEN};border:none;border-radius:8px;"
            f"color:#0d1117;font-size:13px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#00a844;}}"
        )
        v.addWidget(btn_save, alignment=Qt.AlignLeft)
        return f