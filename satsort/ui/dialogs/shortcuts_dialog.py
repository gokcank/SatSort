"""
SatSort - Keyboard Shortcuts Dialog (Cheat Sheet)
Displays categorized shortcuts in a clean, modern layout.
"""

from __future__ import annotations
from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QWidget,
)

from ...i18n import i18n, t


class ShortcutsDialog(QDialog):
    """Modern keyboard shortcuts cheat sheet dialog."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        is_tr = i18n.current_language == "Türkçe"
        self.setWindowTitle("⌨️ " + ("Klavye Kısayolları" if is_tr else "Keyboard Shortcuts"))
        self.resize(540, 480)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        is_tr = i18n.current_language == "Türkçe"

        # Title / Description
        header_lbl = QLabel(
            "⚡ " + ("SatSort Hızlı Erişim Klavye Kısayolları" if is_tr else "SatSort Keyboard Shortcuts Guide")
        )
        header_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(header_lbl)

        # Tab Widget for Categories
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 6px 14px;
                font-weight: bold;
            }
        """)

        file_shortcuts = [
            ("Ctrl + O", "Dosya Aç (.sdx)" if is_tr else "Open SDX File"),
            ("Ctrl + S", "Kaydet" if is_tr else "Save File"),
            ("Ctrl + W", "Listeyi Kapat" if is_tr else "Close List"),
            ("Ctrl + Q", "Uygulamadan Çık" if is_tr else "Quit Application"),
        ]

        edit_shortcuts = [
            ("Alt + Yukarı (Up)", "Seçili Kanalı 1 Sıra Yukarı Taşı" if is_tr else "Move Selected Channel Up"),
            ("Alt + Aşağı (Down)", "Seçili Kanalı 1 Sıra Aşağı Taşı" if is_tr else "Move Selected Channel Down"),
            ("Ctrl + M", "Kanalı Numaraya Taşı (Araya Ekle & Kaydır)" if is_tr else "Move to Slot Number (Insert & Shift)"),
            ("F2", "Kanalı Yeniden Adlandır" if is_tr else "Rename Channel"),
            ("Boşluk (Space)", "Kanal İşaretini Aç/Kapat" if is_tr else "Toggle Channel Checkbox"),
            ("Delete", "Seçili / İşaretli Kanalları Sil" if is_tr else "Delete Selected / Checked Channels"),
            ("Ctrl + A", "Tüm Kanalları İşaretle" if is_tr else "Check All Channels"),
        ]

        nav_tools_shortcuts = [
            ("Ctrl + F", "Arama Çubuğuna Odaklan" if is_tr else "Focus Search Bar"),
            ("Escape", "Aramayı Temizle / İptal" if is_tr else "Clear Search / Dismiss"),
            ("F4", "Sağ Bilgi Panelini Aç/Kapat" if is_tr else "Toggle Details Panel"),
            ("Ctrl + K", "İki Listeyi Karşılaştır" if is_tr else "Compare Two Files"),
            ("Ctrl + I", "Farklı Dosyadan Kanalları İçe Aktar" if is_tr else "Import Channels from File"),
            ("Ctrl + /", "Klavye Kısayolları Bilgi Penceresi" if is_tr else "Show Keyboard Shortcuts"),
            ("F1", "SatSort Hakkında" if is_tr else "About SatSort"),
        ]

        tabs.addTab(self._create_shortcut_table(edit_shortcuts, is_tr), "✏️ " + ("Düzenleme & Sıralama" if is_tr else "Editing & Sorting"))
        tabs.addTab(self._create_shortcut_table(file_shortcuts, is_tr), "📁 " + ("Dosya İşlemleri" if is_tr else "File Operations"))
        tabs.addTab(self._create_shortcut_table(nav_tools_shortcuts, is_tr), "🔍 " + ("Arama & Araçlar" if is_tr else "Search & Tools"))

        layout.addWidget(tabs, stretch=1)

        # Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Kapat" if is_tr else "Close")
        btn_close.setStyleSheet("padding: 8px 24px; font-weight: bold;")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)

        layout.addLayout(btn_box)

    def _create_shortcut_table(self, shortcuts: List[Tuple[str, str]], is_tr: bool) -> QWidget:
        table = QTableWidget(len(shortcuts), 2)
        table.setHorizontalHeaderLabels(["Kısayol Tuşu" if is_tr else "Shortcut", "İşlev" if is_tr else "Description"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

        for row, (key, desc) in enumerate(shortcuts):
            key_item = QTableWidgetItem(f"  {key}  ")
            key_item.setTextAlignment(Qt.AlignCenter)
            key_item.setFlags(Qt.ItemIsEnabled)

            desc_item = QTableWidgetItem(desc)
            desc_item.setFlags(Qt.ItemIsEnabled)

            table.setItem(row, 0, key_item)
            table.setItem(row, 1, desc_item)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(4, 8, 4, 4)
        lay.addWidget(table)
        return container
