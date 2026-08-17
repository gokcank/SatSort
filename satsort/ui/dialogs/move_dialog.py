"""
SatSort - Move & Swap Position Dialog
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QMessageBox,
)

from ...i18n import t


class MovePositionDialog(QDialog):
    """Dialog prompting the user for a target channel position/number."""

    def __init__(self, title: str, max_count: int, initial_pos: int = 1, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(320, 160)
        self._max_count = max_count

        self._setup_ui(initial_pos)

    def _setup_ui(self, initial_pos: int) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Label
        lbl = QLabel(t("T146") + f" (1 - {self._max_count}):")  # Pozisyon / Position
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        # Position SpinBox
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, max(1, self._max_count))
        self.spin_box.setValue(max(1, min(initial_pos, self._max_count)))
        self.spin_box.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.spin_box)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_ok = QPushButton(t("T147"))  # Tamam / OK
        self.btn_ok.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton(t("T107"))  # Kapat / Cancel
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _on_accept(self) -> None:
        pos = self.spin_box.value()
        if pos < 1 or pos > self._max_count:
            QMessageBox.warning(self, "SatSort", t("T148"))  # Geçersiz pozisyon değeri
            return
        self.accept()

    def get_target_index(self) -> int:
        """Returns the 0-based target index."""
        return self.spin_box.value() - 1
