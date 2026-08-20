"""
SatSort - Move Position Dialog (Insert & Shift)
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QMessageBox,
)

from ...i18n import t, i18n


class MovePositionDialog(QDialog):
    """Dialog prompting the user for a target channel position/number with insert & shift."""

    def __init__(
        self,
        title: str,
        max_count: int,
        initial_pos: int = 1,
        channel_name: Optional[str] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(380, 220)
        self._max_count = max_count
        self._channel_name = channel_name
        self._initial_pos = initial_pos

        self._setup_ui(initial_pos)

    def _setup_ui(self, initial_pos: int) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(12)

        is_tr = i18n.current_language == "Türkçe"

        # Channel Info Banner if provided
        if self._channel_name:
            info_lbl = QLabel(
                f"<b>{'Kanal' if is_tr else 'Channel'}:</b> {self._channel_name} "
                f"<span style='color: #94a3b8;'>({'Mevcut Sıra' if is_tr else 'Current Slot'}: {self._initial_pos})</span>"
            )
            info_lbl.setStyleSheet("font-size: 13px; color: #38bdf8;")
            info_lbl.setWordWrap(True)
            layout.addWidget(info_lbl)

        # Target Slot Label
        lbl = QLabel(
            ("Hedef Sıra Numarası" if is_tr else "Target Slot Number") + f" (1 - {self._max_count}):"
        )
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        # Position SpinBox
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, max(1, self._max_count))
        self.spin_box.setValue(max(1, min(initial_pos, self._max_count)))
        self.spin_box.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.spin_box)

        # Helper note explaining Insert & Shift behavior
        hint_lbl = QLabel(
            "ℹ️ " + ("Kanal seçilen sıraya yerleştirilecek, diğer kanallar güvenle aşağı kaydırılacaktır."
                     if is_tr else "Channel will be inserted at this slot, subsequent channels will shift down.")
        )
        hint_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        hint_lbl.setWordWrap(True)
        layout.addWidget(hint_lbl)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_ok = QPushButton(t("T147"))  # Tamam / OK
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton(t("T107"))  # Kapat / Cancel
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        # Auto-focus and select all in spinbox for rapid typing
        QTimer.singleShot(50, lambda: (self.spin_box.setFocus(), self.spin_box.selectAll()))

    def _on_accept(self) -> None:
        pos = self.spin_box.value()
        if pos < 1 or pos > self._max_count:
            QMessageBox.warning(self, "SatSort", t("T148"))  # Geçersiz pozisyon değeri
            return
        self.accept()

    def get_target_index(self) -> int:
        """Returns the 0-based target index."""
        return self.spin_box.value() - 1
