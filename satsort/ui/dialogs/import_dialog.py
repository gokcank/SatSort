"""
SatSort - Import Channels From Another SatcoDX File Dialog (Form4)
"""

from __future__ import annotations
import os
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from ...core.models import Channel
from ...core.parser import read_sdx_file
from ...i18n import t
from ..channel_table import ChannelTableWidget
from ..search_bar import SearchBarWidget


class ImportChannelsDialog(QDialog):
    """Dialog for browsing a secondary .sdx file and selecting channels to copy to the active list."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T103"))  # Çoklu İşlemler / Multiple Operations
        self.resize(750, 600)
        self._selected_channels_to_import: List[Channel] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title & Info Card
        lbl_title = QLabel(t("T105"))  # Farklı Dosyadan Kanal Kopyalama
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(t("T166"))  # Açıklama metni
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_desc)

        # File Load Bar
        file_bar = QHBoxLayout()
        self.btn_load = QPushButton("📂 " + t("T163"))  # SatcoDx Dosyası Yükleyin
        self.btn_load.clicked.connect(self._on_load_file)
        file_bar.addWidget(self.btn_load)

        self.lbl_loaded_file = QLabel("")
        self.lbl_loaded_file.setStyleSheet("color: #34d399; font-weight: bold;")
        file_bar.addWidget(self.lbl_loaded_file, stretch=1)

        layout.addLayout(file_bar)

        # Search Bar
        self.search_bar = SearchBarWidget()
        self.search_bar.text_changed.connect(self._on_search_changed)
        self.search_bar.search_confirmed.connect(self._on_search_confirmed)
        self.search_bar.clear_requested.connect(self._on_search_cleared)
        layout.addWidget(self.search_bar)

        # Channel Table
        self.table = ChannelTableWidget()
        layout.addWidget(self.table)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_uncheck = QPushButton("⚪ " + t("T161"))  # Tüm Seçimleri Kaldır
        self.btn_uncheck.setProperty("class", "secondary")
        self.btn_uncheck.clicked.connect(self.table.uncheck_all)
        btn_bar.addWidget(self.btn_uncheck)

        btn_bar.addStretch()

        self.btn_copy = QPushButton("📥 " + t("T162"))  # Kanal Listesine Kopyala
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        btn_bar.addWidget(self.btn_copy)

        self.btn_close = QPushButton(t("T107"))  # Kapat
        self.btn_close.setProperty("class", "secondary")
        self.btn_close.clicked.connect(self.reject)
        btn_bar.addWidget(self.btn_close)

        layout.addLayout(btn_bar)

    def _on_load_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("T163"),
            "",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            channels = read_sdx_file(file_path)
            self.table.set_channels(channels)
            self.lbl_loaded_file.setText(f"{os.path.basename(file_path)} ({len(channels)} {t('T118')})")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")

    def _on_search_changed(self, query: str) -> None:
        channels = self.table.get_channels()
        matches = [ch for ch in channels if query.lower() in ch.channel_name.lower()]
        self.search_bar.set_match_count(len(matches), len(channels))

    def _on_search_confirmed(self, query: str) -> None:
        channels = self.table.get_channels()
        count = 0
        for ch in channels:
            if query.lower() in ch.channel_name.lower():
                ch.is_checked = True
                count += 1
        self.table.set_channels(channels)
        self.search_bar.set_match_count(count, len(channels))

    def _on_search_cleared(self) -> None:
        self.search_bar.set_match_count(0, len(self.table.get_channels()))

    def _on_copy_clicked(self) -> None:
        checked = self.table.get_checked_channels()
        if not checked:
            # Fallback to selected row if no checkboxes checked
            sel = self.table.get_selected_channel()
            if sel:
                checked = [sel]

        if not checked:
            QMessageBox.warning(self, "SatSort", "Lütfen kopyalanacak kanalları seçin.")
            return

        self._selected_channels_to_import = checked
        self.accept()

    def get_selected_channels(self) -> List[Channel]:
        return self._selected_channels_to_import
