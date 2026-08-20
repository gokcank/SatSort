"""
SatSort - Reference List Sort Dialog
Allows user to pick a reference .sdx list to automatically reorder the current channel list.
"""

from __future__ import annotations
import os
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)

from ...core.models import Channel
from ...core.parser import read_sdx_file
from ...core.reference_sorter import sort_channels_by_reference
from ...i18n import t, i18n


class ReferenceSortDialog(QDialog):
    """Interactive dialog for selecting a reference list and applying automatic sorting."""

    sorting_applied = Signal(list)  # Emits sorted List[Channel]

    def __init__(self, current_channels: List[Channel], parent=None) -> None:
        super().__init__(parent)
        self._current_channels = current_channels
        self._sorted_channels: Optional[List[Channel]] = None

        is_tr = i18n.current_language == "Türkçe"
        self.setWindowTitle("🔗 " + ("Referans Liste ile Sırala" if is_tr else "Sort by Reference List"))
        self.resize(560, 420)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        is_tr = i18n.current_language == "Türkçe"

        # Description
        desc_lbl = QLabel(
            ("Eski veya düzenli bir <b>.sdx</b> dosyasını referans seçerek, mevcut açık listedeki "
             "kanalları tek tıkla referans dosyanızdaki sıralamaya göre otomatik dizin." if is_tr
             else "Select an existing sorted <b>.sdx</b> file to automatically reorder the open channel list."))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        layout.addWidget(desc_lbl)

        # File Selection Box
        file_box = QHBoxLayout()
        file_box.setSpacing(10)
        self.btn_select_file = QPushButton("📂 " + ("Referans Dosyası Seç (.sdx)..." if is_tr else "Select Reference File (.sdx)..."))
        self.btn_select_file.setStyleSheet("padding: 8px 14px; font-weight: bold;")
        self.btn_select_file.clicked.connect(self._on_select_file)
        file_box.addWidget(self.btn_select_file)

        self.lbl_selected_file = QLabel("Seçilen Dosya: Yok" if is_tr else "Selected File: None")
        self.lbl_selected_file.setStyleSheet("color: #94a3b8; font-size: 12px;")
        file_box.addWidget(self.lbl_selected_file, stretch=1)
        layout.addLayout(file_box)

        # Status & Stats Banner
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background-color: #1e293b; border-radius: 8px; padding: 10px;")
        stats_layout = QVBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(10, 8, 10, 8)
        stats_layout.setSpacing(6)

        self.lbl_match_stats = QLabel("Lütfen yukarıdan bir referans .sdx dosyası seçin." if is_tr else "Please select a reference .sdx file above.")
        self.lbl_match_stats.setStyleSheet("font-size: 13px; font-weight: bold; color: #f8fafc;")
        stats_layout.addWidget(self.lbl_match_stats)

        self.lbl_unmatched_note = QLabel("")
        self.lbl_unmatched_note.setStyleSheet("font-size: 11px; color: #94a3b8;")
        stats_layout.addWidget(self.lbl_unmatched_note)
        layout.addWidget(self.stats_frame)

        # Preview Table
        lbl_preview = QLabel("Önizleme (İlk 10 Kanal):" if is_tr else "Preview (First 10 Channels):")
        lbl_preview.setStyleSheet("font-size: 12px; font-weight: bold; color: #94a3b8;")
        layout.addWidget(lbl_preview)

        self.preview_table = QTableWidget(0, 3)
        self.preview_table.setHorizontalHeaderLabels(["#", "Kanal Adı" if is_tr else "Channel Name", "Frekans" if is_tr else "Frequency"])
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.preview_table.setColumnWidth(0, 50)
        self.preview_table.setColumnWidth(2, 90)
        self.preview_table.setFixedHeight(140)
        layout.addWidget(self.preview_table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_apply = QPushButton("✅ " + ("Sıralamayı Uygula" if is_tr else "Apply Sorting"))
        self.btn_apply.setEnabled(False)
        self.btn_apply.setStyleSheet("padding: 8px 18px; font-weight: bold;")
        self.btn_apply.clicked.connect(self._on_apply)
        btn_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton(t("T107"))  # İptal / Cancel
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _on_select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Referans SDX Dosyası Seç" if i18n.current_language == "Türkçe" else "Select Reference SDX File",
            "",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            ref_channels = read_sdx_file(file_path)
            if not ref_channels:
                QMessageBox.warning(self, "SatSort", "Referans dosyasında kanal bulunamadı!" if i18n.current_language == "Türkçe" else "No channels found in reference file!")
                return

            sorted_res, matched, unmatched = sort_channels_by_reference(self._current_channels, ref_channels)
            self._sorted_channels = sorted_res

            is_tr = i18n.current_language == "Türkçe"
            self.lbl_selected_file.setText(f"{os.path.basename(file_path)} ({len(ref_channels)} {t('T118')})")

            match_pct = int((matched / len(self._current_channels)) * 100) if self._current_channels else 0
            self.lbl_match_stats.setText(
                f"✅ Eşleşen: {matched} / {len(self._current_channels)} (%{match_pct})" if is_tr
                else f"✅ Matched: {matched} / {len(self._current_channels)} ({match_pct}%)"
            )
            self.lbl_unmatched_note.setText(
                f"ℹ️ {unmatched} adet yeni/eşleşmeyen kanal listenin sonuna eklenecektir." if is_tr
                else f"ℹ️ {unmatched} unmatched/new channels will be placed at the end."
            )

            # Populate preview table
            self.preview_table.setRowCount(0)
            for i, ch in enumerate(sorted_res[:10]):
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)
                self.preview_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
                self.preview_table.setItem(row, 1, QTableWidgetItem(ch.channel_name))
                self.preview_table.setItem(row, 2, QTableWidgetItem(ch.frequency))

            self.btn_apply.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Referans dosya okunamadı: {e}")

    def _on_apply(self) -> None:
        if self._sorted_channels:
            self.sorting_applied.emit(self._sorted_channels)
            self.accept()
