# -*- coding: utf-8 -*-
"""
pages/userProfile/crop_dialog.py
Dialog untuk crop foto profil berbentuk lingkaran.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


BG        = "#0A1123"
CARD      = "#1A2332"
BORDER    = "#1e3a50"
TEXT1     = "#e8eaf0"
TEXT2     = "#8899aa"
ACCENT    = "#4ADE80"
ACCENT_HV = "#16a34a"
DANGER    = "#e74c3c"


class CropCanvas(QtWidgets.QWidget):
    """
    Widget canvas untuk preview dan drag gambar di dalam area crop lingkaran.
    """

    def __init__(self, pixmap: QtGui.QPixmap, parent=None):
        super().__init__(parent)
        self.setFixedSize(340, 340)
        self.setStyleSheet(f"background-color: #0d1520; border-radius: 8px;")

        self._original = pixmap
        self._scale    = 1.0
        self._offset   = QtCore.QPointF(0, 0)
        self._drag_start = None
        self._offset_start = None

        # Ukuran area crop lingkaran
        self.CIRCLE_R = 140
        self.CENTER   = QtCore.QPointF(170, 170)

        self._fit_image()

    def _fit_image(self):
        """Sesuaikan skala awal agar gambar mengisi area lingkaran."""
        w = self._original.width()
        h = self._original.height()
        diameter = self.CIRCLE_R * 2
        self._scale = max(diameter / w, diameter / h) * 1.0
        self._center_image()

    def _center_image(self):
        """Posisikan gambar di tengah canvas."""
        sw = self._original.width()  * self._scale
        sh = self._original.height() * self._scale
        self._offset = QtCore.QPointF(
            self.CENTER.x() - sw / 2,
            self.CENTER.y() - sh / 2
        )

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        # Background
        p.fillRect(self.rect(), QtGui.QColor("#0d1520"))

        # Gambar yang bisa digeser
        sw = int(self._original.width()  * self._scale)
        sh = int(self._original.height() * self._scale)
        scaled_px = self._original.scaled(
            sw, sh,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        p.drawPixmap(int(self._offset.x()), int(self._offset.y()), scaled_px)

        # Overlay gelap di luar lingkaran
        overlay = QtGui.QPixmap(self.size())
        overlay.fill(QtCore.Qt.transparent)
        op = QtGui.QPainter(overlay)
        op.setRenderHint(QtGui.QPainter.Antialiasing)
        op.fillRect(overlay.rect(), QtGui.QColor(0, 0, 0, 160))
        op.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        op.setBrush(QtCore.Qt.black)
        op.setPen(QtCore.Qt.NoPen)
        op.drawEllipse(
            QtCore.QPointF(self.CENTER.x(), self.CENTER.y()),
            self.CIRCLE_R, self.CIRCLE_R
        )
        op.end()
        p.drawPixmap(0, 0, overlay)

        # Border lingkaran
        pen = QtGui.QPen(QtGui.QColor(ACCENT))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawEllipse(
            QtCore.QPointF(self.CENTER.x(), self.CENTER.y()),
            self.CIRCLE_R, self.CIRCLE_R
        )

        p.end()

    def wheelEvent(self, event):
        """Zoom in/out dengan scroll mouse."""
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        new_scale = self._scale * factor

        # Batasi skala minimum agar gambar selalu mengisi lingkaran
        min_scale = max(
            (self.CIRCLE_R * 2) / self._original.width(),
            (self.CIRCLE_R * 2) / self._original.height()
        )
        self._scale = max(min_scale, min(new_scale, min_scale * 5))
        self._clamp_offset()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start    = event.pos()
            self._offset_start  = QtCore.QPointF(self._offset)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.pos() - self._drag_start
            self._offset = self._offset_start + QtCore.QPointF(delta)
            self._clamp_offset()
            self.update()

    def mouseReleaseEvent(self, event):
        self._drag_start = None
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    def _clamp_offset(self):
        """Pastikan gambar selalu menutupi area lingkaran."""
        sw = self._original.width()  * self._scale
        sh = self._original.height() * self._scale

        left_limit  = self.CENTER.x() - self.CIRCLE_R - sw + self.CIRCLE_R
        right_limit = self.CENTER.x() + self.CIRCLE_R - self.CIRCLE_R
        top_limit   = self.CENTER.y() - self.CIRCLE_R - sh + self.CIRCLE_R
        bot_limit   = self.CENTER.y() + self.CIRCLE_R - self.CIRCLE_R

        ox = max(left_limit, min(self._offset.x(), right_limit))
        oy = max(top_limit,  min(self._offset.y(), bot_limit))
        self._offset = QtCore.QPointF(ox, oy)

    def get_cropped_pixmap(self) -> QtGui.QPixmap:
        """Ambil hasil crop berbentuk lingkaran."""
        size = self.CIRCLE_R * 2

        # Render canvas ke pixmap
        canvas_px = QtGui.QPixmap(self.size())
        self.render(canvas_px)

        # Crop area lingkaran dari canvas
        cx = int(self.CENTER.x() - self.CIRCLE_R)
        cy = int(self.CENTER.y() - self.CIRCLE_R)
        cropped = canvas_px.copy(cx, cy, size, size)

        # Terapkan mask lingkaran agar hasilnya benar-benar bulat
        result = QtGui.QPixmap(size, size)
        result.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(result)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(cropped))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        return result


class CropDialog(QtWidgets.QDialog):
    """
    Dialog crop foto profil.
    Gunakan .get_result() untuk mendapatkan QPixmap hasil crop.
    """

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._result_pixmap = None
        self._build_ui(image_path)

    def _build_ui(self, image_path: str):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        # Card wrapper
        card = QtWidgets.QWidget()
        card.setObjectName("cropCard")
        card.setStyleSheet(f"""
            QWidget#cropCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Judul
        title = QtWidgets.QLabel("Edit Foto Profil")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {TEXT1}; font-size: 16px;
            font-weight: bold; font-family: 'Segoe UI';
        """)
        layout.addWidget(title)

        # Subjudul
        hint = QtWidgets.QLabel("Geser gambar • Scroll untuk zoom")
        hint.setAlignment(QtCore.Qt.AlignCenter)
        hint.setStyleSheet(f"color: {TEXT2}; font-size: 11px; font-family: 'Segoe UI';")
        layout.addWidget(hint)

        # Canvas crop
        pixmap = QtGui.QPixmap(image_path)
        self.canvas = CropCanvas(pixmap)
        self.canvas.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        layout.addWidget(self.canvas, alignment=QtCore.Qt.AlignCenter)

        # Tombol
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(12)

        btn_batal = QtWidgets.QPushButton("Batal")
        btn_batal.setFixedHeight(40)
        btn_batal.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_batal.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT1}; font-size: 13px;
                font-weight: bold; font-family: 'Segoe UI';
                border: 1px solid {BORDER}; border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {CARD};
                border-color: {TEXT2};
            }}
        """)
        btn_batal.clicked.connect(self.reject)

        btn_simpan = QtWidgets.QPushButton("Gunakan Foto")
        btn_simpan.setFixedHeight(40)
        btn_simpan.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_simpan.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: #0F1621; font-size: 13px;
                font-weight: bold; font-family: 'Segoe UI';
                border: none; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_HV}; }}
        """)
        btn_simpan.clicked.connect(self._on_simpan)

        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        layout.addLayout(btn_row)

        outer.addWidget(card)

    def _on_simpan(self):
        self._result_pixmap = self.canvas.get_cropped_pixmap()
        self.accept()

    def get_result(self) -> QtGui.QPixmap | None:
        """Kembalikan QPixmap hasil crop, atau None jika dibatalkan."""
        return self._result_pixmap
