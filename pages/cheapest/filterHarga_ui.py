"""
filterHarga_ui.py
─────────────────
PyQt5 UI untuk halaman "Filter Berdasarkan Harga".
Design reference: Screenshot images
Code style reference: dashboard_ui.py & popular_ui.py
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QCursor, QPalette, QIcon

from widget.navbar import Navbar
from widget.cardGame import PopularGameCard, COVER_RATIO, INFO_H
from pages.cheapest.filterHarga_logic import (
    get_games_by_price, filter_games_by_price, search_games, 
    parse_price_input, fmt_price
)

# ── Colour Palette ────────────────────────────────────────────────────────
BG        = "#0A1123"
BG2       = "#1A1F36"
CARD      = "#1A2332"
CARD_HOV  = "#1A2332"
ACCENT    = "#39d353"
ACCENT2   = "#2ea84a"
TEXT1     = "#e8eaf0"
TEXT2     = "#8899aa"
BORDER    = "#1e3a50"
TAG_BG    = "#162840"
INPUT_BG  = "#1e2a3e"
BUTTON_PRESET = "#1a3350"

# ── Layout constants ──────────────────────────────────────────────────────
COLS = 5
GAP = 14


# ── Price Range Buttons ───────────────────────────────────────────────────
class PriceRangeButton(QPushButton):
    """Tombol preset range harga seperti '< 50.000', '50.000 - 200.000', dll."""
    
    def __init__(self, label, min_price, max_price):
        super().__init__(label)
        self.min_price = min_price
        self.max_price = max_price
        self.setFixedHeight(36)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._set_normal_style()
    
    def _set_normal_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {BUTTON_PRESET};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {CARD_HOV};
                border-color: {ACCENT2};
            }}
        """)
    
    def _set_active_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-weight: bold;
            }}
        """)
    
    def set_active(self, active):
        if active:
            self._set_active_style()
        else:
            self._set_normal_style()


# ── Filter Panel ──────────────────────────────────────────────────────────
class FilterPanel(QFrame):
    """Panel filter harga dengan input min/max dan tombol preset."""
    
    filter_applied = pyqtSignal(int, object)  # (min_price, max_price or None)
    filter_reset = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setObjectName("FilterPanel")
        self.setStyleSheet(f"""
            QFrame#FilterPanel {{
                background: {BORDER};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        
        self._active_preset = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(8)
        
        icon_label = QLabel()
        icon_label.setPixmap(
            QIcon("assets/filter_outline.png").pixmap(20, 20)
        )
        icon_label.setFixedSize(20, 20)
        header.addWidget(icon_label)
        
        title = QLabel("Filter Berdasarkan Harga")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT1}; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # ── Input Row: Min - Max ──────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        
        # Min price
        min_container = QVBoxLayout()
        min_container.setSpacing(6)
        min_label = QLabel("Harga Minimum (Rp)")
        min_label.setFont(QFont("Segoe UI", 9))
        min_label.setStyleSheet(f"color: {TEXT2}; background: transparent;")
        min_container.addWidget(min_label)
        
        self.min_input = QLineEdit()
        self.min_input.setPlaceholderText("0")
        self.min_input.setFont(QFont("Segoe UI", 10))
        self.min_input.setFixedHeight(40)
        self.min_input.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_BG};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT};
            }}
        """)
        min_container.addWidget(self.min_input)
        input_row.addLayout(min_container)
        
        # Separator
        sep = QLabel("–")
        sep.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sep.setStyleSheet(f"color: {TEXT2}; background: transparent;")
        sep.setAlignment(Qt.AlignCenter)
        sep.setFixedWidth(20)
        input_row.addWidget(sep, alignment=Qt.AlignBottom)
        
        # Max price
        max_container = QVBoxLayout()
        max_container.setSpacing(6)
        max_label = QLabel("Harga Maximum (Rp)")
        max_label.setFont(QFont("Segoe UI", 9))
        max_label.setStyleSheet(f"color: {TEXT2}; background: transparent;")
        max_container.addWidget(max_label)
        
        self.max_input = QLineEdit()
        self.max_input.setPlaceholderText("Tidak terbatas")
        self.max_input.setFont(QFont("Segoe UI", 10))
        self.max_input.setFixedHeight(40)
        self.max_input.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_BG};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT};
            }}
        """)
        max_container.addWidget(self.max_input)
        input_row.addLayout(max_container)
        
        layout.addLayout(input_row)
        
        # ── Preset Buttons ────────────────────────────────────────────────
        preset_row = QHBoxLayout()
        preset_row.setSpacing(10)
        
        self.preset_buttons = []
        
        # < 50.000
        btn1 = PriceRangeButton("< 50.000", 0, 49999)
        btn1.clicked.connect(lambda: self._on_preset_clicked(btn1))
        preset_row.addWidget(btn1)
        self.preset_buttons.append(btn1)
        
        # 50.000 - 200.000
        btn2 = PriceRangeButton("50.000 - 200.000", 50000, 200000)
        btn2.clicked.connect(lambda: self._on_preset_clicked(btn2))
        preset_row.addWidget(btn2)
        self.preset_buttons.append(btn2)
        
        # > 200.000
        btn3 = PriceRangeButton("> 200.000", 200001, None)
        btn3.clicked.connect(lambda: self._on_preset_clicked(btn3))
        preset_row.addWidget(btn3)
        self.preset_buttons.append(btn3)
        
        layout.addLayout(preset_row)
        
        # ── Action Buttons ────────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        
        self.apply_btn = QPushButton("Terapkan Filter")
        self.apply_btn.setFixedHeight(40)
        self.apply_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.apply_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {ACCENT2};
            }}
        """)
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        action_row.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setFont(QFont("Segoe UI", 10))
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BUTTON_PRESET};
                color: {TEXT1};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {CARD_HOV};
                border-color: {ACCENT2};
            }}
        """)
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        action_row.addWidget(self.reset_btn)
        
        layout.addLayout(action_row)
        
        # ── Result Label ──────────────────────────────────────────────────
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Segoe UI", 9))
        self.result_label.setStyleSheet(f"color: {TEXT2}; background: transparent;")
        layout.addWidget(self.result_label)
    
    def _on_preset_clicked(self, btn):
        """Handler ketika preset button diklik."""
        # Reset semua button
        for b in self.preset_buttons:
            b.set_active(False)
        
        # Aktifkan button yang diklik
        btn.set_active(True)
        self._active_preset = btn
        
        # Set input fields
        self.min_input.setText(str(btn.min_price))
        if btn.max_price is None:
            self.max_input.setText("")
        else:
            self.max_input.setText(str(btn.max_price))
    
    def _on_apply_clicked(self):
        """Handler ketika tombol Terapkan Filter diklik."""
        min_price = parse_price_input(self.min_input.text())
        max_price = parse_price_input(self.max_input.text())
        
        # Default min = 0 jika kosong
        if min_price is None:
            min_price = 0
        
        self.filter_applied.emit(min_price, max_price)
    
    def _on_reset_clicked(self):
        """Handler ketika tombol Reset diklik."""
        self.min_input.setText("")
        self.max_input.setText("")
        
        # Reset preset buttons
        for b in self.preset_buttons:
            b.set_active(False)
        self._active_preset = None
        
        self.result_label.setText("")
        self.filter_reset.emit()
    
    def set_result_text(self, text):
        """Set text hasil filter."""
        self.result_label.setText(text)


# ── Games Grid ────────────────────────────────────────────────────────────
class GamesGrid(QWidget):
    """Grid untuk menampilkan card game."""
    
    card_clicked = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.cards = []
        self.setStyleSheet(f"background: {BG};")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 10, 20, 20)
        outer.setSpacing(8)
        
        self.count_lbl = QLabel("Menampilkan 0 game")
        self.count_lbl.setFont(QFont("Segoe UI", 9))
        self.count_lbl.setStyleSheet(f"color: {TEXT2}; padding-left: 4px;")
        outer.addWidget(self.count_lbl)
        
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: transparent;")
        outer.addWidget(self.canvas)
        outer.addStretch()
    
    def populate(self, games):
        """Populate grid dengan list game."""
        # Clear existing cards
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []
        
        if not games:
            self.count_lbl.setText("Tidak ada game yang ditemukan")
            self.canvas.setFixedHeight(10)
            return
        
        self.count_lbl.setText(f"Menampilkan {len(games)} game")
        
        for g in games:
            card = PopularGameCard(g)
            card.setParent(self.canvas)
            card.show()
            card.clicked.connect(self.card_clicked)
            self.cards.append(card)
        
        self._relayout()
    
    def _relayout(self):
        """Re-calculate layout posisi cards."""
        if not self.cards:
            self.canvas.setFixedHeight(10)
            return
        
        avail = self.canvas.width()
        if avail < 50:
            avail = self.width() - 40
        if avail < 50:
            return
        
        card_w = max(120, (avail - GAP * (COLS - 1)) // COLS)
        cover_h = int(card_w * COVER_RATIO)
        card_h = cover_h + INFO_H
        
        for i, card in enumerate(self.cards):
            row, col = divmod(i, COLS)
            x = col * (card_w + GAP)
            y = row * (card_h + GAP)
            card.set_width(card_w)
            card.move(x, y)
        
        rows = (len(self.cards) + COLS - 1) // COLS
        total_h = rows * card_h + (rows - 1) * GAP + 4
        self.canvas.setFixedHeight(total_h)
    
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout()


# ── Hero Banner ───────────────────────────────────────────────────────────
class HeroBanner(QWidget):
    """Banner header halaman."""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(105)
        self.setStyleSheet(f"background: {BG};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 16)
        layout.setSpacing(4)
        
        title = QLabel("Temukan Game Terbaik dengan Harga Terbaik")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT1};")
        layout.addWidget(title)
        
        subtitle = QLabel("Cari game dengan harga terbaik di waktu yang tepat")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {TEXT2};")
        layout.addWidget(subtitle)


# ── Main Window ───────────────────────────────────────────────────────────
class FilterHargaWindow(QWidget):
    """Main window untuk halaman Filter Harga."""
    
    card_clicked = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self._all_games = []
        self._filtered_games = []
        self._current_min = 0
        self._current_max = None
        
        self.setStyleSheet(f"background: {BG};")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ── Navbar ────────────────────────────────────────────────────────
        self.nav = Navbar(active_page="filter_harga")
        self.nav.setAttribute(Qt.WA_StyledBackground, True)
        self.nav.setStyleSheet("background: #000000;")
        root.addWidget(self.nav)
        
        # ── Hero Banner ───────────────────────────────────────────────────
        self.hero = HeroBanner()
        root.addWidget(self.hero)
        
        # ── Filter Panel ──────────────────────────────────────────────────
        filter_container = QWidget()
        filter_container.setStyleSheet(f"background: {BG};")
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setContentsMargins(20, 0, 20, 12)
        filter_layout.setSpacing(0)
        
        self.filter_panel = FilterPanel()
        filter_layout.addWidget(self.filter_panel)
        root.addWidget(filter_container)
        
        # ── Scroll Area + Games Grid ──────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {BG}; border: none; }}
            QScrollBar:vertical {{
                background: {CARD}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {ACCENT2}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        
        self.grid = GamesGrid()
        self.grid.card_clicked.connect(self.card_clicked)
        scroll.setWidget(self.grid)
        root.addWidget(scroll)
        
        # ── Connect Signals ───────────────────────────────────────────────
        self.filter_panel.filter_applied.connect(self._on_filter_applied)
        self.filter_panel.filter_reset.connect(self._on_filter_reset)
        self.nav.search_changed.connect(self._on_search_changed)
        
        # Load semua game (tanpa filter)
        self._load_all_games()
    
    def _load_all_games(self):
        """Load semua game dari database (tanpa filter)."""
        # Ambil semua game dengan harga >= 0
        self._all_games = get_games_by_price(min_price=0, max_price=None)
        self._filtered_games = self._all_games
        self.grid.populate(self._all_games)
    
    def _on_filter_applied(self, min_price, max_price):
        """Handler ketika filter diterapkan."""
        self._current_min = min_price
        self._current_max = max_price
        
        # Ambil dari database
        self._filtered_games = get_games_by_price(min_price, max_price)
        self.grid.populate(self._filtered_games)
        
        # Update result label
        if max_price is None:
            range_text = f"Rp{min_price:,} - Tidak terbatas".replace(",", ".")
        else:
            range_text = f"Rp{min_price:,} - Rp{max_price:,}".replace(",", ".")
        
        self.filter_panel.set_result_text(
            f"Menampilkan {len(self._filtered_games)} game dengan harga {range_text}"
        )
    
    def _on_filter_reset(self):
        """Handler ketika filter direset."""
        self._current_min = 0
        self._current_max = None
        self._load_all_games()
    
    def _on_search_changed(self, query):
        """Handler ketika search query berubah."""
        if not query.strip():
            # Jika query kosong, tampilkan hasil filter terakhir
            self.grid.populate(self._filtered_games)
        else:
            # Filter dari hasil yang sudah difilter
            searched = search_games(self._filtered_games, query)
            self.grid.populate(searched)
