from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QPainter

class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str,
                 confirm_text: str = "Ya",
                 cancel_text: str = "Batal",
                 danger: bool = True,
                 parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        if parent:
            self.setFixedSize(parent.size())
        self._result = False
        self._build_ui(title, message, confirm_text, cancel_text, danger)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 128))
        p.end()

    def _build_ui(self, title, message, confirm_text, cancel_text, danger):
        wrapper = QWidget(self)
        wrapper.setObjectName("dlgWrapper")
        wrapper.setFixedWidth(480)
        wrapper.setStyleSheet("""
            QWidget#dlgWrapper {
                background-color: #1A2332;
                border: 1px solid #2A3647;
                border-radius: 12px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        wrapper.setGraphicsEffect(shadow)

        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.setAlignment(Qt.AlignCenter)
        outerLayout.addWidget(wrapper)

        innerLayout = QVBoxLayout(wrapper)
        innerLayout.setContentsMargins(40, 36, 40, 32)
        innerLayout.setSpacing(16)

        titleLabel = QLabel(title)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet(
            "color: #FFFFFF; font-size: 16px; font-weight: bold; font-family: Arial;"
        )
        innerLayout.addWidget(titleLabel)

        msgLabel = QLabel(message)
        msgLabel.setAlignment(Qt.AlignCenter)
        msgLabel.setWordWrap(True)
        msgLabel.setStyleSheet(
            "color: #8899aa; font-size: 13px; font-family: Arial;"
        )
        innerLayout.addWidget(msgLabel)

        btnRow = QHBoxLayout()
        btnRow.setSpacing(12)

        confirm_style = """
            QPushButton { background-color: #E81B1B; color: #FFFFFF; font-size: 13px;
                          font-weight: bold; font-family: Arial; border: none; border-radius: 8px; }
        """ if danger else """
            QPushButton { background-color: #2A3050; color: #0F1621; font-size: 13px;
                          font-weight: bold; font-family: Arial; border: none; border-radius: 8px; }
            QPushButton:hover { background-color: #16a34a; }
        """

        btnConfirm = QPushButton(confirm_text)
        btnConfirm.setFixedHeight(40)
        btnConfirm.setCursor(QCursor(Qt.PointingHandCursor))
        btnConfirm.setStyleSheet(confirm_style)
        btnConfirm.clicked.connect(self._on_confirm)

        btnCancel = QPushButton(cancel_text)
        btnCancel.setFixedHeight(40)
        btnCancel.setCursor(QCursor(Qt.PointingHandCursor))
        btnCancel.setStyleSheet("""
            QPushButton { background-color: #2A3050; color: #FFFFFF; font-size: 13px;
                        font-weight: bold; font-family: Arial;
                        border: none; border-radius: 8px; }
        """)
        btnCancel.clicked.connect(self._on_cancel)

        btnRow.addWidget(btnConfirm)
        btnRow.addWidget(btnCancel)
        innerLayout.addLayout(btnRow)

    def _on_confirm(self):
        self._result = True
        self.accept()

    def _on_cancel(self):
        self._result = False
        self.reject()

    def confirmed(self) -> bool:
        return self._result