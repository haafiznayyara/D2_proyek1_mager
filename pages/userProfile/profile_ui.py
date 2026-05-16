import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets  
from widget.navbar import Navbar

STYLESHEET = """
QMainWindow {
    background-color: #0A1123;
}
QWidget#centralwidget {
    background-color: #0A1123;
}

/* ===== BACK BUTTON ===== */
QPushButton#btnBack {
    color: #8B96A5;
    font-size: 13px;
    font-family: 'Segoe UI';
    background: transparent;
    border: none;
    text-align: left;
    padding: 4px 0px;
}
QPushButton#btnBack:hover {
    color: #FFFFFF;
}

/* ===== LEFT PANEL ===== */
QWidget#leftPanel {
    background-color: #1A2332;
    border-radius: 12px;
}
QLabel#panelTitle {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Segoe UI';
}
QLabel#avatarLabel {
    color: #FFFFFF;
    font-size: 36px;
    font-weight: bold;
    font-family: 'Segoe UI';
    background-color: #2A3647;
    border-radius: 50px;
    min-width: 100px;
    max-width: 100px;
    min-height: 100px;
    max-height: 100px;
}
QLabel#fieldLabel, QLabel#fieldLabel_2 {
    color: #8B96A5;
    font-size: 11px;
    font-family: 'Segoe UI';
}
QLineEdit#displayNameEdit {
    background-color: #1A1F36;
    border: 1px solid #2A3050;
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 13px;
    font-family: 'Segoe UI';
    padding: 6px 10px;
}
QLineEdit#usernameEdit {
    background-color: transparent;
    border: 1px solid #2A3050;
    border-radius: 6px;
    color: #8B96A5;
    font-size: 13px;
    font-family: 'Segoe UI';
    padding: 6px 10px;
}
QPushButton#btnSave {
    background-color: #4ADE80;
    color: #0F1621;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnSave:hover {
    background-color: #16a34a;
}
QLabel#sectionLabel {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    font-family: 'Segoe UI';
}
QLabel#emptyLabel {
    color: #515050;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QPushButton#btnLogout {
    background-color: #5c1a1a;
    color: #e05555;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnLogout:hover {
    background-color: #701f1f;
}

/* ===== RIGHT CARDS ===== */
QWidget#cardLike, QWidget#cardDislike, QWidget#cardKomentar, QWidget#cardWishlist {
    background-color: #1A2332;
    border-radius: 12px;
}
QLabel#cardTotal {
    color: #8B96A5;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QLabel#cardEmpty, QLabel#cardLikeEmpty, QLabel#cardDislikeEmpty,
QLabel#cardKomentarEmpty {
    color: #515050;
    font-size: 12px;
    font-family: 'Segoe UI';
}
QPushButton#btnWishlist {
    background-color: #4ADE80;
    color: #0F1621;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI';
    border: none;
    border-radius: 8px;
    padding: 10px;
}
QPushButton#btnWishlist:hover {
    background-color: #16a34a;
}
"""


def icon_path(filename):
    """Resolve path ikon dari folder assets."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "..", "assets", filename)


def make_icon_label(png_file, size=20):
    """Buat QLabel yang menampilkan ikon PNG dengan ukuran tetap."""
    lbl = QtWidgets.QLabel()
    lbl.setFixedSize(size, size)
    lbl.setScaledContents(True)
    pixmap = QtGui.QPixmap(icon_path(png_file))
    lbl.setPixmap(pixmap)
    return lbl


class ProfileWindow(QtWidgets.QMainWindow):
    # Signal khusus jika diperlukan untuk pindah ke wishlist langsung dari profile
    wishlist_clicked = QtCore.pyqtSignal() 
    back_clicked = QtCore.pyqtSignal()
    logout_clicked = QtCore.pyqtSignal()

    def _on_save_clicked(self):
        new_username = self.usernameEdit.text().strip()
        if not new_username:
            return
        self.displayNameEdit.setText(new_username)
        self.avatarLabel.setText(new_username[0].upper())

    def load_user(self, user: dict):
        username = user.get("username", "")
        self.displayNameEdit.setText(username)
        self.usernameEdit.setText(username)
        # Set huruf pertama sebagai avatar
        self.avatarLabel.setText(username[0].upper() if username else "?")

    def update_wishlist_count(self, jumlah: int):
        for lbl in self.cardWishlist.findChildren(QtWidgets.QLabel):
            if lbl.text().startswith("Total:"):
                lbl.setText(f"Total: {jumlah} Game")
                break

    def __init__(self):
        super().__init__()
        self.setObjectName("ProfileWindow")
        self.resize(1100, 700)
        self.setWindowTitle("MAGER - Profil User")
        self.setStyleSheet(STYLESHEET)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        # ── Root layout ──────────────────────────────────────────────────────
        self.mainVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)

        # ── NAVBAR ───────────────────────────────────────────────────────────
        # Active page di-set ke profile
        self.nav = Navbar(active_page="profile")
        self.mainVLayout.addWidget(self.nav)

        # ── CONTENT AREA ─────────────────────────────────────────────────────
        self.contentWidget = QtWidgets.QWidget()
        contentVLayout = QtWidgets.QVBoxLayout(self.contentWidget)
        contentVLayout.setContentsMargins(24, 16, 24, 24)
        contentVLayout.setSpacing(16)

        # Back button
        self.btnBack = QtWidgets.QPushButton("← Kembali")
        self.btnBack.setObjectName("btnBack")
        self.btnBack.setMaximumWidth(120)
        contentVLayout.addWidget(self.btnBack)
        self.btnBack.clicked.connect(self.back_clicked.emit)

        # Main content row
        mainContentLayout = QtWidgets.QHBoxLayout()
        mainContentLayout.setSpacing(16)

        # ── LEFT PANEL ───────────────────────────────────────────────────────
        self.leftPanel = QtWidgets.QWidget()
        self.leftPanel.setObjectName("leftPanel")
        self.leftPanel.setMinimumWidth(260)
        self.leftPanel.setMaximumWidth(280)

        leftPanelLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        leftPanelLayout.setContentsMargins(20, 20, 20, 20)
        leftPanelLayout.setSpacing(12)

        self.panelTitle = QtWidgets.QLabel("Profil Saya")
        self.panelTitle.setObjectName("panelTitle")
        leftPanelLayout.addWidget(self.panelTitle)

        # Avatar (centered)
        avatarLayout = QtWidgets.QHBoxLayout()
        self.avatarLabel = QtWidgets.QLabel("D")
        self.avatarLabel.setObjectName("avatarLabel")
        self.avatarLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.avatarLabel.setFixedSize(100, 100)
        avatarLayout.addStretch()
        avatarLayout.addWidget(self.avatarLabel)
        avatarLayout.addStretch()
        leftPanelLayout.addLayout(avatarLayout)

        # Display Name
        self.fieldLabel = QtWidgets.QLabel("Display Name")
        self.fieldLabel.setObjectName("fieldLabel")
        self.displayNameEdit = QtWidgets.QLineEdit("Dago Keren")
        self.displayNameEdit.setObjectName("displayNameEdit")
        leftPanelLayout.addWidget(self.fieldLabel)
        leftPanelLayout.addWidget(self.displayNameEdit)

        # Username
        self.fieldLabel_2 = QtWidgets.QLabel("Username")
        self.fieldLabel_2.setObjectName("fieldLabel_2")
        self.usernameEdit = QtWidgets.QLineEdit()
        self.usernameEdit.setObjectName("usernameEdit")
        self.usernameEdit.setPlaceholderText("Dago")
        leftPanelLayout.addWidget(self.fieldLabel_2)
        leftPanelLayout.addWidget(self.usernameEdit)

        # Save button
        self.btnSave = QtWidgets.QPushButton("Simpan Perubahan")
        self.btnSave.setObjectName("btnSave")
        leftPanelLayout.addWidget(self.btnSave)
        self.btnSave.clicked.connect(self._on_save_clicked)

        # Statistik Preferensi
        self.sectionLabel = QtWidgets.QLabel("Statistik Preferensi")
        self.sectionLabel.setObjectName("sectionLabel")
        leftPanelLayout.addWidget(self.sectionLabel)

        leftPanelLayout.addSpacerItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        )

        self.emptyLabel = QtWidgets.QLabel("Belum ada data preferensi game")
        self.emptyLabel.setObjectName("emptyLabel")
        self.emptyLabel.setAlignment(QtCore.Qt.AlignCenter)
        leftPanelLayout.addWidget(self.emptyLabel)

        leftPanelLayout.addStretch()

        # Logout button with icon
        self.btnLogout = QtWidgets.QPushButton("  Logout")
        self.btnLogout.setObjectName("btnLogout")
        self.btnLogout.setIcon(QtGui.QIcon(icon_path("material-symbols_logout-rounded.png")))
        self.btnLogout.setIconSize(QtCore.QSize(18, 18))
        self.btnLogout.clicked.connect(self.logout_clicked.emit)
        leftPanelLayout.addWidget(self.btnLogout)

        mainContentLayout.addWidget(self.leftPanel)

        # ── RIGHT PANEL — 2×2 card grid ──────────────────────────────────────
        cardsGridLayout = QtWidgets.QGridLayout()
        cardsGridLayout.setSpacing(16)

        # Helper: build a card widget
        def make_card(obj_name, icon_png, title_text, title_color,
                      total_text, empty_text, extra_widget=None):
            card = QtWidgets.QWidget()
            card.setObjectName(obj_name)
            vbox = QtWidgets.QVBoxLayout(card)
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(8)

            # Title row: icon + label
            title_row = QtWidgets.QHBoxLayout()
            title_row.setSpacing(8)
            icon_lbl = make_icon_label(icon_png, 20)
            title_lbl = QtWidgets.QLabel(title_text)
            title_lbl.setStyleSheet(
                f"color: {title_color}; font-size: 16px; font-weight: bold; font-family: 'Segoe UI';"
            )
            title_row.addWidget(icon_lbl)
            title_row.addWidget(title_lbl)
            title_row.addStretch()
            vbox.addLayout(title_row)

            # Total label
            total_lbl = QtWidgets.QLabel(total_text)
            total_lbl.setStyleSheet("color: #8B96A5; font-size: 12px; font-family: 'Segoe UI';")
            vbox.addWidget(total_lbl)

            vbox.addStretch()

            # Empty label
            empty_lbl = QtWidgets.QLabel(empty_text)
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #515050; font-size: 12px; font-family: 'Segoe UI';")
            vbox.addWidget(empty_lbl)

            vbox.addStretch()

            if extra_widget:
                vbox.addWidget(extra_widget)

            return card

        # Card: Riwayat Like (0,0)
        self.cardLike = make_card(
            "cardLike", "Vector.png", "Riwayat Like", "#FFFFFF",
            "Total: 0 Game", "Belum ada game yang di-like"
        )

        # Card: Riwayat Dislike (0,1)
        self.cardDislike = make_card(
            "cardDislike", "Vector (2).png", "Riwayat Dislike", "#FFFFFF",
            "Total: 0 Game", "Belum ada game yang di-dislike"
        )

        # Card: Riwayat Komentar (1,0)
        self.cardKomentar = make_card(
            "cardKomentar", "Vector (1).png", "Riwayat Komentar", "#FFFFFF",
            "Total: 0 Game", "Belum ada komentar"
        )

        # Card: Riwayat Wishlist (1,1) — has extra button
        self.btnWishlist = QtWidgets.QPushButton("Lihat Wishlist")
        self.btnWishlist.setObjectName("btnWishlist")
        # Hubungkan tombol ini dengan signal
        self.btnWishlist.clicked.connect(self.wishlist_clicked.emit) 
        self.btnWishlist.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.cardWishlist = make_card(
            "cardWishlist", "Vector (3).png", "Riwayat Wishlist", "#FFFFFF",
            "Total: 0 Game", "", extra_widget=self.btnWishlist
        )

        cardsGridLayout.addWidget(self.cardLike,     0, 0)
        cardsGridLayout.addWidget(self.cardDislike,  0, 1)
        cardsGridLayout.addWidget(self.cardKomentar, 1, 0)
        cardsGridLayout.addWidget(self.cardWishlist, 1, 1)

        mainContentLayout.addLayout(cardsGridLayout)
        contentVLayout.addLayout(mainContentLayout)
        self.mainVLayout.addWidget(self.contentWidget)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ProfileWindow()
    window.show()
    sys.exit(app.exec_())