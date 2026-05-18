import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

class PriceGraphCanvas(FigureCanvas):
    def __init__(self, parent=None):
        # Menggunakan warna dari palette MAGER kamu
        bg_color = '#1A2332'  # BG_CARD
        grid_color = '#2A3647' # BORDER
        text_color = '#7b8db0' # MUTED
        line_color = '#4ADE80' # GREEN

        fig, self.ax = plt.subplots(figsize=(7, 3), dpi=100)
        fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        super(PriceGraphCanvas, self).__init__(fig)
        self.setParent(parent)

        self.line_color = line_color
        self.grid_color = grid_color
        self.text_color = text_color

        # Tampilan default saat data belum diload
        self.plot_history([], [])

    def plot_history(self, dates, prices):
        self.ax.clear()
        
        if not dates or not prices:
            # Jika belum ada data
            self.ax.text(0.5, 0.5, "Memuat Riwayat Harga...", 
                         color=self.text_color, ha='center', va='center', transform=self.ax.transAxes)
            self.ax.axis('off')
            self.draw()
            return

        # Plot garis riwayat harga
        self.ax.plot(dates, prices, color=self.line_color, linewidth=2.5, marker='o', markersize=4)
        
        # Pengaturan Grid
        self.ax.grid(True, color=self.grid_color, linestyle='--', linewidth=0.5)
        
        # Pengaturan warna teks Sumbu X dan Y
        self.ax.tick_params(axis='x', colors=self.text_color, labelsize=9)
        self.ax.tick_params(axis='y', colors=self.text_color, labelsize=9)
        
        # Pengaturan warna border grafik
        for spine in self.ax.spines.values():
            spine.set_color(self.grid_color)

        # Format Sumbu Y (Rp ...K)
        def rupiah_formatter(x, pos):
            if x == 0: return "Gratis"
            return f'Rp {int(x/1000)}K'
        self.ax.yaxis.set_major_formatter(FuncFormatter(rupiah_formatter))

        # Format Sumbu X (Misal: 12 Mei)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        
        self.figure.tight_layout()
        self.draw()