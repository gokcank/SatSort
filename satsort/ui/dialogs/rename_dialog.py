"""
SatSort - Rename Channel Dialog
"""

from __future__ import annotations
import re
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from ...core.parser import validate_channel_name, normalize_turkish_chars
from ...i18n import t


class RenameChannelDialog(QDialog):
    """Dialog for editing and validating a channel name with max 16-character limit."""

    def __init__(self, current_name: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T116"))  # Kanal Adını Değiştir / Change Channel Name
        self.setFixedSize(360, 180)
        self._setup_ui(current_name)

    def _setup_ui(self, current_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header with char counter
        header_layout = QHBoxLayout()
        lbl_title = QLabel(t("T123") + ":")  # Kanal Adı
        lbl_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_layout.addWidget(lbl_title)

        self.lbl_char_count = QLabel("0 / 16")
        self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header_layout.addWidget(self.lbl_char_count, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)

        # Name input field
        self.txt_name = QLineEdit()
        self.txt_name.setMaxLength(16)
        self.txt_name.setText(current_name)
        self.txt_name.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        self.txt_name.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.txt_name)

        self._on_text_changed(current_name)

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

    def _on_text_changed(self, text: str) -> None:
        count = len(text)
        self.lbl_char_count.setText(f"{count} / 16")
        if count == 16:
            self.lbl_char_count.setStyleSheet("color: #f59e0b; font-size: 12px; font-weight: bold;")
        else:
            self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 12px;")

    def _on_accept(self) -> None:
        raw_name = self.txt_name.text().strip()

        if not raw_name:
            QMessageBox.warning(self, "SatSort", t("T149"))  # Kanal adı boş olamaz
            return

        if len(raw_name) > 16:
            QMessageBox.warning(self, "SatSort", t("T150"))  # 16 karakterden uzun olamaz
            return

        # Check character validity (normalized)
        normalized = normalize_turkish_chars(raw_name).lower()
        if re.search(r"[^a-z0-9\s+_\-\.\/]", normalized):
            QMessageBox.warning(self, "SatSort", t("T151"))  # Sadece harf ve rakam
            return

        self.accept()

    def get_channel_name(self) -> str:
        return self.txt_name.text().strip()
