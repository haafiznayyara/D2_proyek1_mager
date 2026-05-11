import sys
from pages.wishlist.wishlist_logic import WishlistLogic, fetch_wishlist
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QColor, QPalette

from pages.dashboard.dashboard_logic import get_games_from_db, BG, CARD, ACCENT, TEXT1
from pages.dashboard.dashboard_ui import MainWindow
from pages.popular.popular_ui import PopularGamesWindow
from pages.gameProfile.profileGame_ui import GameDetailWindow
from pages.wishlist.wishlist_ui import WishlistWindow
from pages.wishlist.wishlist_logic import WishlistLogic
from pages.userProfile.profile_ui import ProfileWindow
from pages.auth.auth_ui import LoginWindow, RegisterWindow, SuccessRegisterPage
from pages.cheapest.filterHarga_logic import (
        get_games_by_price, filter_games_by_price, search_games, parse_price_input)
from pages.cheapest.filterHarga_ui import FilterHargaWindow 


def build_dark_palette():
    dark = QPalette()
    for role, color in [
        (QPalette.Window,          BG),
        (QPalette.WindowText,      TEXT1),
        (QPalette.Base,            CARD),
        (QPalette.AlternateBase,   BG),
        (QPalette.Text,            TEXT1),
        (QPalette.Button,          CARD),
        (QPalette.ButtonText,      TEXT1),
        (QPalette.Highlight,       ACCENT),
        (QPalette.HighlightedText, "#000"),
    ]:
        dark.setColor(role, QColor(color))
    return dark


class Router(QStackedWidget):
    """
    Pusat navigasi multipage MAGER.
    Index halaman:
        0 → Dashboard
        1 → Game Detail
        2 → Wishlist
        3 → Profile
        4 → Login
        5 → Register
        6 → Success
        7 → Popular
        8 → Filter Harga
    """

    PAGE_DASHBOARD = 0
    PAGE_DETAIL    = 1
    PAGE_WISHLIST  = 2
    PAGE_PROFILE   = 3
    PAGE_LOGIN     = 4
    PAGE_REGISTER  = 5   
    PAGE_SUCCESS   = 6
    PAGE_POPULAR   = 7
    PAGE_FILTER_HARGA = 8

    def _on_add_to_wishlist(self, game: dict):
        self.wishlist_logic.on_add_clicked(game)
        self.wishlist_logic.load_wishlist()

    def __init__(self, games):
        super().__init__()
        self.setWindowTitle("MAGER — Game Store")
        self.resize(1100, 820)
        self.setMinimumSize(900, 640)

        # ── Buat semua halaman ──────────────────────────────────────────
        self.current_user = None   # diisi saat login berhasil

        self.page_dashboard = MainWindow(games)
        self.page_detail    = GameDetailWindow()
        self.page_wishlist  = WishlistWindow()
        self.page_profile   = ProfileWindow()
        self.page_login    = LoginWindow()
        self.page_register = RegisterWindow()
        self.page_success = SuccessRegisterPage()
        self.page_popular = PopularGamesWindow()
        self.page_filter_harga = FilterHargaWindow()
        
        self.addWidget(self.page_dashboard)      # index 0
        self.addWidget(self.page_detail)         # index 1
        self.addWidget(self.page_wishlist)       # index 2
        self.addWidget(self.page_profile)        # index 3
        self.addWidget(self.page_login)          # index 4
        self.addWidget(self.page_register)       # index 5
        self.addWidget(self.page_success)        # index 6
        self.addWidget(self.page_popular)        # index 7
        self.addWidget(self.page_filter_harga)   # index 8

        #ROUTE DASHBOARD
        self.page_dashboard.nav.dashboard_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_dashboard.nav.wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_dashboard.nav.profile_clicked.connect(
            lambda: self.go_to(self.PAGE_PROFILE)
        )
        self.page_dashboard.nav.popular_clicked.connect(
            lambda: self.go_to(self.PAGE_POPULAR)
        )
        self.page_dashboard.nav.cheapest_clicked.connect(
            lambda: self.go_to(self.PAGE_FILTER_HARGA)
        )
        self.page_dashboard.card_clicked.connect(self._open_detail)
        self.page_popular.grid.card_clicked.connect(self._open_detail)

        # Game Detail → kembali
        self.page_detail.back_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_detail.nav_wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_detail.nav_profile_clicked.connect(
            lambda: self.go_to(self.PAGE_PROFILE)
        )

        # ROUTE WISHLIST
        self.page_wishlist.nav.popular_clicked.connect(
            lambda: self.go_to(self.PAGE_POPULAR)
        )
        self.page_wishlist.nav.cheapest_clicked.connect(
            lambda: self.go_to(self.PAGE_FILTER_HARGA)
        )
        self.page_wishlist.nav.wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_wishlist.nav.profile_clicked.connect(
            lambda: self.go_to(self.PAGE_PROFILE)
        )
        self.page_wishlist.nav.dashboard_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )

        # WishlistLogic — dibuat setelah login (lihat _on_login)
        self.wishlist_logic = None

        # ROUTE PROFILE
        self.page_profile.back_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_profile.nav.wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_profile.nav.dashboard_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_profile.nav.popular_clicked.connect(
            lambda: self.go_to(self.PAGE_POPULAR)
        )
        
        #ROUTE POPULAR
        self.page_popular.nav.dashboard_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_popular.nav.wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_popular.nav.profile_clicked.connect(
            lambda: self.go_to(self.PAGE_PROFILE)
        )
        self.page_popular.nav.cheapest_clicked.connect(
            lambda: self.go_to(self.PAGE_FILTER_HARGA)
        )
        
        #ROUTE FILTER HARGA
        self.page_filter_harga.nav.dashboard_clicked.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        self.page_filter_harga.nav.popular_clicked.connect(
            lambda: self.go_to(self.PAGE_POPULAR)
        )
        self.page_filter_harga.nav.wishlist_clicked.connect(
            lambda: self.go_to(self.PAGE_WISHLIST)
        )
        self.page_filter_harga.nav.profile_clicked.connect(
            lambda: self.go_to(self.PAGE_PROFILE)
        )
        self.page_filter_harga.nav.cheapest_clicked.connect(
            lambda: self.go_to(self.PAGE_FILTER_HARGA)
        )
        self.page_filter_harga.card_clicked.connect(self._open_detail)
        
        self.page_login.login_success.connect(lambda user: self._on_login(user))
        self.page_login.go_register.connect(lambda: self.go_to(self.PAGE_REGISTER))
        self.page_register.go_login.connect(lambda: self.go_to(self.PAGE_LOGIN))
        self.page_register.register_success.connect(self._on_register_success)
        self.page_success.go_login.connect(lambda: self.go_to(self.PAGE_LOGIN))
        
        self.setCurrentIndex(self.PAGE_LOGIN)

    # ── Navigasi ────────────────────────────────────────────────────────
    def go_to(self, index: int):
        if self.currentIndex() != index:
            self.setCurrentIndex(index)
            
    def _on_login(self, user: dict):
        print(f"[DEBUG] Login berhasil: {user}")
        self.current_user = user
        self.page_profile.load_user(user) 
        # Inisialisasi WishlistLogic dengan id_user yang baru login
        id_user = user.get("id_user", 1)
        self.wishlist_logic = WishlistLogic(self.page_wishlist, id_user)

        # Navigasi: "Jelajahi Game" & "← Kembali" → Dashboard
        self.wishlist_logic.go_to_dashboard.connect(
            lambda: self.go_to(self.PAGE_DASHBOARD)
        )
        # Tombol 🗑 pada tiap card → hapus dari DB lalu refresh
        self.page_wishlist.delete_requested.connect(
            self.wishlist_logic.on_delete_clicked
        )
        self.page_dashboard.wishlist_clicked.connect(
            self._on_add_to_wishlist
        )
        self.wishlist_logic.wishlist_count_changed.connect(
            self.page_profile.update_wishlist_count
        )
        self.page_profile.update_wishlist_count(
            len(fetch_wishlist(id_user))
        )

        self.go_to(self.PAGE_DASHBOARD)

    def _on_register_success(self):
        self.go_to(self.PAGE_SUCCESS)
        self.page_success.show_and_redirect()

    def _on_logout(self):
        print("[DEBUG] Logout: sesi dihapus")
        if self.wishlist_logic is not None:
            try:
                self.page_wishlist.delete_requested.disconnect(
                    self.wishlist_logic.on_delete_clicked
                )
                self.wishlist_logic.go_to_dashboard.disconnect()
            except TypeError:
                pass
            self.wishlist_logic = None
        self.current_user = None
        self.go_to(self.PAGE_LOGIN)

    def _open_detail(self, game: dict):
        """Buka halaman detail dengan data game yang diklik."""
        self.page_detail.load_game(game)
        self.go_to(self.PAGE_DETAIL)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(build_dark_palette())

    games = get_games_from_db()

    router = Router(games)
    router.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()