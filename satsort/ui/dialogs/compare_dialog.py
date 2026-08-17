"""
SatSort - Compare Two SatcoDX Files Dialog (Form5)
"""

from __future__ import annotations
import os
from typing import List, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QMessageBox,
)

from ...core.models import Channel
from ...core.parser import read_sdx_file
from ...i18n import t


class CompareFilesDialog(QDialog):
    """Dialog for comparing the active channel list with an external .sdx file."""

    apply_removals = Signal(list)  # List[Channel] to remove from main list
    apply_additions = Signal(list) # List[Channel] to add to main list

    def __init__(self, current_channels: List[Channel], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T104"))  # Karşılaştırma / Compare
        self.resize(800, 600)
        self._current_channels = current_channels
        self._removed_channels: List[Channel] = []
        self._inserted_channels: List[Channel] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Info Card
        lbl_title = QLabel(t("T159"))  # Kanallar Arası Farklar
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(t("T167"))  # Karşılaştırma açıklaması
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_desc)

        # Compare File Selector Bar
        top_bar = QHBoxLayout()
        self.btn_choose_file = QPushButton("🔍 " + t("T160"))  # Karşılaştır
        self.btn_choose_file.clicked.connect(self._on_choose_and_compare)
        top_bar.addWidget(self.btn_choose_file)

        self.lbl_file_info = QLabel("Henüz dosya seçilmedi")
        self.lbl_file_info.setStyleSheet("color: #94a3b8;")
        top_bar.addWidget(self.lbl_file_info, stretch=1)
        layout.addLayout(top_bar)

        # Tabs for Removed vs Inserted
        self.tabs = QTabWidget()

        # Tab 1: Removed Channels (Silinenler)
        tab_rem = QWidget()
        layout_rem = QVBoxLayout(tab_rem)
        self.table_removed = self._create_diff_table()
        layout_rem.addWidget(self.table_removed)

        self.btn_remove_selected = QPushButton("❌ " + t("T164"))  # Silinen Seçili Kanalları Çıkart
        self.btn_remove_selected.clicked.connect(self._on_remove_channels_clicked)
        layout_rem.addWidget(self.btn_remove_selected)
        self.tabs.addTab(tab_rem, "🗑️ " + t("T157"))  # Silinen Kanallar

        # Tab 2: Inserted Channels (Yeni Eklenenler)
        tab_ins = QWidget()
        layout_ins = QVBoxLayout(tab_ins)
        self.table_inserted = self._create_diff_table()
        layout_ins.addWidget(self.table_inserted)

        self.btn_insert_selected = QPushButton("➕ " + t("T165"))  # Yeni Eklenenleri Ekle
        self.btn_insert_selected.clicked.connect(self._on_insert_channels_clicked)
        layout_ins.addWidget(self.btn_insert_selected)
        self.tabs.addTab(tab_ins, "✨ " + t("T158"))  # Eklenen Kanallar

        layout.addWidget(self.tabs)

        # Bottom Close Button
        btn_bottom = QHBoxLayout()
        btn_bottom.addStretch()
        self.btn_close = QPushButton(t("T107"))  # Kapat
        self.btn_close.setProperty("class", "secondary")
        self.btn_close.clicked.connect(self.accept)
        btn_bottom.addWidget(self.btn_close)
        layout.addLayout(btn_bottom)

    def _create_diff_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["✓", t("T117"), t("T123"), t("T126"), t("T127"), t("T128")])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        return table

    def _on_choose_and_compare(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("T163"),
            "",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            comparison_channels = read_sdx_file(file_path)
            self.lbl_file_info.setText(f"Karşılaştırılan: {os.path.basename(file_path)} ({len(comparison_channels)} {t('T118')})")
            self._compute_differences(comparison_channels)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")

    def _compute_differences(self, new_channels: List[Channel]) -> None:
        """Finds channels present in current but missing in new (removed), and vice-versa (inserted)."""
        current_map = {
            (ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate): ch
            for ch in self._current_channels
        }
        new_map = {
            (ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate): ch
            for ch in new_channels
        }

        self._removed_channels = [ch for key, ch in current_map.items() if key not in new_map]
        self._inserted_channels = [ch for key, ch in new_map.items() if key not in current_map]

        self._populate_table(self.table_removed, self._removed_channels, is_removal=True)
        self._populate_table(self.table_inserted, self._inserted_channels, is_removal=False)

        self.tabs.setTabText(0, f"🗑️ {t('T157')} ({len(self._removed_channels)})")
        self.tabs.setTabText(1, f"✨ {t('T158')} ({len(self._inserted_channels)})")

    def _populate_table(self, table: QTableWidget, channels: List[Channel], is_removal: bool) -> None:
        table.setRowCount(len(channels))
        bg_color = QColor("#2e1010") if is_removal else QColor("#082e1b")

        for row, ch in enumerate(channels):
            item_chk = QTableWidgetItem()
            item_chk.setCheckState(Qt.Checked)
            table.setItem(row, 0, item_chk)

            item_no = QTableWidgetItem(str(row + 1))
            item_no.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, item_no)

            item_name = QTableWidgetItem(ch.channel_name)
            item_name.setFont(QFont("", -1, QFont.Bold))
            table.setItem(row, 2, item_name)

            item_freq = QTableWidgetItem(ch.frequency)
            item_freq.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 3, item_freq)

            pol_str = "V" if ch.polarization.value == "Vertical" else "H"
            item_pol = QTableWidgetItem(pol_str)
            item_pol.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 4, item_pol)

            item_sr = QTableWidgetItem(ch.symbol_rate)
            item_sr.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 5, item_sr)

            for col in range(6):
                it = table.item(row, col)
                if it:
                    it.setBackground(bg_color)

    def _on_remove_channels_clicked(self) -> None:
        checked_channels = []
        for row in range(self.table_removed.rowCount()):
            item = self.table_removed.item(row, 0)
            if item and item.checkState() == Qt.Checked and row < len(self._removed_channels):
                checked_channels.append(self._removed_channels[row])

        if not checked_channels:
            QMessageBox.information(self, "SatSort", "İşaretli silinecek kanal bulunamadı.")
            return

        self.apply_removals.emit(checked_channels)
        QMessageBox.information(self, "SatSort", f"{len(checked_channels)} kanal listeden çıkarıldı.")
        self.accept()

    def _on_insert_channels_clicked(self) -> None:
        checked_channels = []
        for row in range(self.table_inserted.rowCount()):
            item = self.table_inserted.item(row, 0)
            if item and item.checkState() == Qt.Checked and row < len(self._inserted_channels):
                checked_channels.append(self._inserted_channels[row])

        if not checked_channels:
            QMessageBox.information(self, "SatSort", "İşaretli eklenecek kanal bulunamadı.")
            return

        self.apply_additions.emit(checked_channels)
        QMessageBox.information(self, "SatSort", f"{len(checked_channels)} yeni kanal listenize eklendi.")
        self.accept()
