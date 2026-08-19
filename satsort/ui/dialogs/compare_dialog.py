"""
SatSort - 4-Tab Comprehensive Diff & Comparison Engine (Form5)
"""

from __future__ import annotations
import os
from typing import List, Dict, Tuple, Optional

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
    """
    Comprehensive 4-Tab Diff Engine for comparing channel lists:
    1. Order Changes (Sırası Değişenler)
    2. Name Changes (İsmi Değişenler)
    3. Removed Channels (Silinenler)
    4. Added Channels (Yeni Eklenenler)
    """

    apply_removals = Signal(list)   # List[Channel] to remove from main list
    apply_additions = Signal(list)  # List[Channel] to add to main list

    def __init__(self, current_channels: List[Channel], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SatSort - " + t("T104"))  # Karşılaştırma / Compare
        self.resize(950, 650)
        self.setMinimumSize(800, 500)
        self._current_channels = current_channels
        self._comparison_channels: List[Channel] = []

        self._order_changed: List[dict] = []
        self._name_changed: List[dict] = []
        self._removed_channels: List[Channel] = []
        self._inserted_channels: List[Channel] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Info Card
        lbl_title = QLabel("📊 " + t("T159"))  # Kanallar Arası Farklar
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(
            "İki SDX listesi arasındaki sıra değişikliklerini, yeniden adlandırmaları, "
            "silinen ve yeni eklenen tüm kanalları detaylı olarak inceleyin."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_desc)

        # Compare File Selector Bar
        top_bar = QHBoxLayout()
        self.btn_choose_file = QPushButton("🔍 " + t("T160"))  # Dosya Seç ve Karşılaştır
        self.btn_choose_file.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)
        self.btn_choose_file.clicked.connect(self._on_choose_and_compare)
        top_bar.addWidget(self.btn_choose_file)

        self.lbl_file_info = QLabel("Karşılaştırmak için bir .sdx dosyası seçin")
        self.lbl_file_info.setStyleSheet("color: #94a3b8; font-size: 13px;")
        top_bar.addWidget(self.lbl_file_info, stretch=1)
        layout.addLayout(top_bar)

        # Tabs Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #0f172a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #0f172a;
                color: #38bdf8;
                border: 1px solid #334155;
                border-bottom: 1px solid #0f172a;
            }
        """)

        # Tab 1: Order Changed (Sırası Değişenler)
        tab_order = QWidget()
        layout_order = QVBoxLayout(tab_order)
        self.table_order = self._create_table(["Kanal Adı", "Mevcut Sıra", "Karşılaştırılan Sıra", "Fark", "Frekans / Pol"])
        layout_order.addWidget(self.table_order)
        self.tabs.addTab(tab_order, "🔢 Sırası Değişenler (0)")

        # Tab 2: Name Changed (İsmi Değişenler)
        tab_renamed = QWidget()
        layout_renamed = QVBoxLayout(tab_renamed)
        self.table_renamed = self._create_table(["Sıra", "Mevcut İsim", "Yeni Dosyadaki İsim", "Frekans", "Polarizasyon", "SR"])
        layout_renamed.addWidget(self.table_renamed)
        self.tabs.addTab(tab_renamed, "✏️ İsmi Değişenler (0)")

        # Tab 3: Removed Channels (Silinenler)
        tab_rem = QWidget()
        layout_rem = QVBoxLayout(tab_rem)
        self.table_removed = self._create_table(["✓", t("T117"), t("T123"), t("T126"), t("T127"), t("T128")])
        layout_rem.addWidget(self.table_removed)

        self.btn_remove_selected = QPushButton("❌ " + t("T164"))  # Silinen Seçili Kanalları Çıkart
        self.btn_remove_selected.setStyleSheet("background-color: #991b1b; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_remove_selected.clicked.connect(self._on_remove_channels_clicked)
        layout_rem.addWidget(self.btn_remove_selected)
        self.tabs.addTab(tab_rem, "🗑️ " + t("T157") + " (0)")  # Silinen Kanallar

        # Tab 4: Inserted Channels (Yeni Eklenenler)
        tab_ins = QWidget()
        layout_ins = QVBoxLayout(tab_ins)
        self.table_inserted = self._create_table(["✓", t("T117"), t("T123"), t("T126"), t("T127"), t("T128")])
        layout_ins.addWidget(self.table_inserted)

        self.btn_insert_selected = QPushButton("➕ " + t("T165"))  # Yeni Eklenenleri Ekle
        self.btn_insert_selected.setStyleSheet("background-color: #065f46; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_insert_selected.clicked.connect(self._on_insert_channels_clicked)
        layout_ins.addWidget(self.btn_insert_selected)
        self.tabs.addTab(tab_ins, "✨ " + t("T158") + " (0)")  # Eklenen Kanallar

        layout.addWidget(self.tabs)

        # Bottom Close Button
        btn_bottom = QHBoxLayout()
        btn_bottom.addStretch()
        self.btn_close = QPushButton(t("T107"))  # Kapat
        self.btn_close.setStyleSheet("background-color: #334155; color: white; padding: 6px 16px; border-radius: 4px;")
        self.btn_close.clicked.connect(self.accept)
        btn_bottom.addWidget(self.btn_close)
        layout.addLayout(btn_bottom)

    def _create_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        header = table.horizontalHeader()
        for c in range(len(headers)):
            if headers[c] in ["Kanal Adı", "Mevcut İsim", "Yeni Dosyadaki İsim", t("T123")]:
                header.setSectionResizeMode(c, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
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
            self._comparison_channels = comparison_channels
            self.lbl_file_info.setText(f"Karşılaştırılan: {os.path.basename(file_path)} ({len(comparison_channels)} {t('T118')})")
            self._compute_differences(comparison_channels)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")

    def _compute_differences(self, new_channels: List[Channel]) -> None:
        """Computes Order, Rename, Removed, and Inserted differences between lists."""
        current_channels = self._current_channels

        # 1. Maps for exact technical matching
        # Key: (frequency, polarization, symbol_rate, sid, vpid, apid)
        current_tech_map: Dict[tuple, Tuple[int, Channel]] = {}
        for idx, ch in enumerate(current_channels):
            key = (ch.frequency, ch.polarization.value, ch.symbol_rate, ch.sid, ch.vpid, ch.apid)
            current_tech_map[key] = (idx, ch)

        new_tech_map: Dict[tuple, Tuple[int, Channel]] = {}
        for idx, ch in enumerate(new_channels):
            key = (ch.frequency, ch.polarization.value, ch.symbol_rate, ch.sid, ch.vpid, ch.apid)
            new_tech_map[key] = (idx, ch)

        # Name-based key for existence: (name_lower, freq, pol, sr)
        current_name_map = {
            (ch.channel_name.lower().strip(), ch.frequency, ch.polarization.value, ch.symbol_rate): (idx, ch)
            for idx, ch in enumerate(current_channels)
        }
        new_name_map = {
            (ch.channel_name.lower().strip(), ch.frequency, ch.polarization.value, ch.symbol_rate): (idx, ch)
            for idx, ch in enumerate(new_channels)
        }

        # Tab 1: Order Changed (Same name & transponder, different index)
        self._order_changed = []
        for key, (idx_curr, ch_curr) in current_name_map.items():
            if key in new_name_map:
                idx_new, _ = new_name_map[key]
                if idx_curr != idx_new:
                    diff = idx_new - idx_curr
                    self._order_changed.append({
                        "channel": ch_curr,
                        "old_idx": idx_curr + 1,
                        "new_idx": idx_new + 1,
                        "diff": diff,
                    })

        # Tab 2: Name Changed (Same technical parameters, different name)
        self._name_changed = []
        for tech_key, (idx_curr, ch_curr) in current_tech_map.items():
            if tech_key in new_tech_map:
                idx_new, ch_new = new_tech_map[tech_key]
                if ch_curr.channel_name.strip() != ch_new.channel_name.strip():
                    self._name_changed.append({
                        "row": idx_curr + 1,
                        "old_name": ch_curr.channel_name,
                        "new_name": ch_new.channel_name,
                        "channel": ch_curr,
                    })

        # Tab 3: Removed (in current, not in new)
        self._removed_channels = [ch for key, (idx, ch) in current_name_map.items() if key not in new_name_map]

        # Tab 4: Added (in new, not in current)
        self._inserted_channels = [ch for key, (idx, ch) in new_name_map.items() if key not in current_name_map]

        # Populate tables
        self._populate_order_table()
        self._populate_renamed_table()
        self._populate_diff_table(self.table_removed, self._removed_channels, is_removal=True)
        self._populate_diff_table(self.table_inserted, self._inserted_channels, is_removal=False)

        # Update tab headers with badge counts
        self.tabs.setTabText(0, f"🔢 Sırası Değişenler ({len(self._order_changed)})")
        self.tabs.setTabText(1, f"✏️ İsmi Değişenler ({len(self._name_changed)})")
        self.tabs.setTabText(2, f"🗑️ {t('T157')} ({len(self._removed_channels)})")
        self.tabs.setTabText(3, f"✨ {t('T158')} ({len(self._inserted_channels)})")

    def _populate_order_table(self) -> None:
        self.table_order.setRowCount(len(self._order_changed))
        for row, item in enumerate(self._order_changed):
            ch = item["channel"]
            it_name = QTableWidgetItem(ch.channel_name)
            it_name.setFont(QFont("", -1, QFont.Bold))
            self.table_order.setItem(row, 0, it_name)

            it_old = QTableWidgetItem(str(item["old_idx"]))
            it_old.setTextAlignment(Qt.AlignCenter)
            self.table_order.setItem(row, 1, it_old)

            it_new = QTableWidgetItem(str(item["new_idx"]))
            it_new.setTextAlignment(Qt.AlignCenter)
            self.table_order.setItem(row, 2, it_new)

            diff_val = item["diff"]
            diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)
            it_diff = QTableWidgetItem(diff_str)
            it_diff.setTextAlignment(Qt.AlignCenter)
            it_diff.setForeground(QColor("#38bdf8") if diff_val < 0 else QColor("#fb923c"))
            it_diff.setFont(QFont("", -1, QFont.Bold))
            self.table_order.setItem(row, 3, it_diff)

            pol_char = "V" if ch.polarization.value == "Vertical" else "H"
            it_freq = QTableWidgetItem(f"{ch.frequency} {pol_char} / {ch.symbol_rate}")
            it_freq.setTextAlignment(Qt.AlignCenter)
            self.table_order.setItem(row, 4, it_freq)

    def _populate_renamed_table(self) -> None:
        self.table_renamed.setRowCount(len(self._name_changed))
        for row, item in enumerate(self._name_changed):
            ch = item["channel"]
            it_row = QTableWidgetItem(str(item["row"]))
            it_row.setTextAlignment(Qt.AlignCenter)
            self.table_renamed.setItem(row, 0, it_row)

            it_old = QTableWidgetItem(item["old_name"])
            it_old.setFont(QFont("", -1, QFont.Bold))
            it_old.setForeground(QColor("#f87171"))
            self.table_renamed.setItem(row, 1, it_old)

            it_new = QTableWidgetItem(item["new_name"])
            it_new.setFont(QFont("", -1, QFont.Bold))
            it_new.setForeground(QColor("#4ade80"))
            self.table_renamed.setItem(row, 2, it_new)

            it_freq = QTableWidgetItem(ch.frequency)
            it_freq.setTextAlignment(Qt.AlignCenter)
            self.table_renamed.setItem(row, 3, it_freq)

            pol_char = "V" if ch.polarization.value == "Vertical" else "H"
            it_pol = QTableWidgetItem(pol_char)
            it_pol.setTextAlignment(Qt.AlignCenter)
            self.table_renamed.setItem(row, 4, it_pol)

            it_sr = QTableWidgetItem(ch.symbol_rate)
            it_sr.setTextAlignment(Qt.AlignCenter)
            self.table_renamed.setItem(row, 5, it_sr)

    def _populate_diff_table(self, table: QTableWidget, channels: List[Channel], is_removal: bool) -> None:
        table.setRowCount(len(channels))
        bg_color = QColor("#450a0a") if is_removal else QColor("#064e3b")

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


# Alias for backward compatibility
CompareDialog = CompareFilesDialog

