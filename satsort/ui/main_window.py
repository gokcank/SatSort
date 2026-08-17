"""
SatSort - Main Window UI
"""

from __future__ import annotations
import os
from typing import List, Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QToolBar,
)

from ..core.models import Channel
from ..core.parser import read_sdx_file, write_sdx_file, validate_channel_name
from ..i18n import i18n, t
from .channel_table import ChannelTableWidget
from .search_bar import SearchBarWidget
from .sidebar import SidebarWidget


class MainWindow(QMainWindow):
    """Main application window for SatSort SatcoDX channel editor."""

    def __init__(self) -> None:
        super().__init__()
        self._current_file_path: Optional[str] = None
        self._all_channels: List[Channel] = []

        self.setWindowTitle("SatSort - SatcoDX Channel Editor")
        self.resize(1100, 700)
        self.setMinimumSize(800, 500)

        self._setup_ui()
        self._setup_menus_and_toolbars()
        self._setup_status_bar()
        self._connect_signals()

        # Register language callback
        i18n.register_language_changed_callback(self._on_language_changed)

    def _setup_ui(self) -> None:
        # Central widget and horizontal splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self._splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self._splitter)

        # Left/Center Container: Search Bar + Channel Table
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.search_bar = SearchBarWidget()
        left_layout.addWidget(self.search_bar)

        self.channel_table = ChannelTableWidget()
        left_layout.addWidget(self.channel_table)

        self._splitter.addWidget(left_container)

        # Right Sidebar (Parameters + Transponder Packages)
        self.sidebar = SidebarWidget()
        self._splitter.addWidget(self.sidebar)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 1)

    def _setup_menus_and_toolbars(self) -> None:
        # Menu Bar
        menu_bar = self.menuBar()

        # 1. File Menu
        self.menu_file = menu_bar.addMenu(t("T100"))  # Menü / Menu
        self.act_open = QAction("📂 " + t("T101"), self)  # SatcoDx Yükle
        self.act_open.setShortcut(QKeySequence.Open)
        self.act_open.triggered.connect(self.open_file)
        self.menu_file.addAction(self.act_open)

        self.act_save = QAction("💾 " + t("T102"), self)  # Kaydet
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self.save_file)
        self.menu_file.addAction(self.act_save)

        self.menu_file.addSeparator()

        self.act_quit = QAction("🚪 " + t("T107"), self)  # Kapat
        self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_quit.triggered.connect(self.close)
        self.menu_file.addAction(self.act_quit)

        # 2. Edit Menu
        self.menu_edit = menu_bar.addMenu("Düzenle")
        self.act_move_up = QAction("⬆️ " + t("T109"), self)
        self.act_move_up.setShortcut("Alt+Up")
        self.act_move_up.triggered.connect(self.channel_table.move_selected_up)
        self.menu_edit.addAction(self.act_move_up)

        self.act_move_down = QAction("⬇️ " + t("T110"), self)
        self.act_move_down.setShortcut("Alt+Down")
        self.act_move_down.triggered.connect(self.channel_table.move_selected_down)
        self.menu_edit.addAction(self.act_move_down)

        self.menu_edit.addSeparator()

        self.act_del_sel = QAction("🗑️ " + t("T111"), self)
        self.act_del_sel.setShortcut(QKeySequence.Delete)
        self.act_del_sel.triggered.connect(self.channel_table.delete_selected)
        self.menu_edit.addAction(self.act_del_sel)

        self.act_del_chk = QAction("❌ " + t("T112"), self)
        self.act_del_chk.triggered.connect(self.channel_table.delete_checked)
        self.menu_edit.addAction(self.act_del_chk)

        self.menu_edit.addSeparator()

        self.act_uncheck_all = QAction("⚪ " + t("T108"), self)
        self.act_uncheck_all.triggered.connect(self.channel_table.uncheck_all)
        self.menu_edit.addAction(self.act_uncheck_all)

        # 3. Tools Menu
        self.menu_tools = menu_bar.addMenu(t("T103"))  # Çoklu İşlemler
        self.act_compare = QAction("📊 " + t("T104"), self)  # Karşılaştırma
        self.menu_tools.addAction(self.act_compare)

        self.act_import = QAction("📥 " + t("T105"), self)  # Farklı Dosyadan Kopyalama
        self.menu_tools.addAction(self.act_import)

        # 4. View Menu
        self.menu_view = menu_bar.addMenu("Görünüm")
        self.act_toggle_sidebar = QAction("📑 " + t("T119"), self, checkable=True)
        self.act_toggle_sidebar.setChecked(True)
        self.act_toggle_sidebar.toggled.connect(self.toggle_sidebar)
        self.menu_view.addAction(self.act_toggle_sidebar)

        # 5. Language Menu
        self.menu_lang = menu_bar.addMenu("🌐 " + t("T168"))
        self._rebuild_language_menu()

        # 6. Help Menu
        self.menu_help = menu_bar.addMenu("Yardım")
        self.act_about = QAction("ℹ️ " + t("T106"), self)
        self.act_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.act_about)

        # Top Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(self.act_open)
        self.toolbar.addAction(self.act_save)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_move_up)
        self.toolbar.addAction(self.act_move_down)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_del_sel)
        self.toolbar.addAction(self.act_uncheck_all)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_compare)
        self.toolbar.addAction(self.act_import)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_toggle_sidebar)

    def _rebuild_language_menu(self) -> None:
        self.menu_lang.clear()
        for lang in i18n.get_supported_languages():
            act = QAction(lang, self, checkable=True)
            act.setChecked(lang == i18n.current_language)
            act.triggered.connect(lambda checked, l=lang: i18n.set_language(l))
            self.menu_lang.addAction(act)

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_file_info = QLabel("Hazır")
        self.lbl_channel_count = QLabel("Kanal: 0 | İşaretli: 0")

        self.status_bar.addWidget(self.lbl_file_info, stretch=1)
        self.status_bar.addPermanentWidget(self.lbl_channel_count)

    def _connect_signals(self) -> None:
        self.channel_table.channels_updated.connect(self._update_channel_counts)
        self.channel_table.channel_selected.connect(self._on_channel_selected)
        self.sidebar.transponder_channel_clicked.connect(self._on_transponder_channel_clicked)
        self.search_bar.text_changed.connect(self._on_search_text_changed)
        self.search_bar.search_confirmed.connect(self._on_search_confirmed)
        self.search_bar.clear_requested.connect(self._on_search_cleared)

    def _on_channel_selected(self, channel: Channel) -> None:
        self.sidebar.set_channel(channel, self.channel_table.get_channels())

    def _on_transponder_channel_clicked(self, channel: Channel) -> None:
        channels = self.channel_table.get_channels()
        try:
            row = channels.index(channel)
            self.channel_table.selectRow(row)
        except ValueError:
            pass

    def _update_channel_counts(self) -> None:
        channels = self.channel_table.get_channels()
        checked_count = len([ch for ch in channels if ch.is_checked])
        self.lbl_channel_count.setText(f"{t('T118')}: {len(channels)} | İşaretli: {checked_count}")
        selected_ch = self.channel_table.get_selected_channel()
        if selected_ch:
            self.sidebar.set_channel(selected_ch, channels)

    def _on_search_text_changed(self, text: str) -> None:
        channels = self.channel_table.get_channels()
        lower_q = text.lower()
        match_count = 0
        for ch in channels:
            if lower_q in ch.channel_name.lower():
                match_count += 1
        self.search_bar.set_match_count(match_count, len(channels))

    def _on_search_confirmed(self, text: str) -> None:
        """Marks matching channels as checked (mimics original Form1 behavior)."""
        channels = self.channel_table.get_channels()
        lower_q = text.lower()
        match_count = 0

        for ch in channels:
            if lower_q in ch.channel_name.lower():
                ch.is_checked = True
                match_count += 1

        self.channel_table.set_channels(channels)
        self.search_bar.set_match_count(match_count, len(channels))

        if match_count == 0:
            QMessageBox.information(self, "SatSort", t("T142"))  # Kanal bulunamadı
        else:
            QMessageBox.information(
                self, "SatSort", f"{match_count} {t('T143')}"  # X Kanal bulundu ve işaretlendi
            )

    def _on_search_cleared(self) -> None:
        self.search_bar.set_match_count(0, len(self.channel_table.get_channels()))

    def open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("T101"),
            "",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            channels = read_sdx_file(file_path)
            self._current_file_path = file_path
            self._all_channels = channels
            self.channel_table.set_channels(channels)
            self.setWindowTitle(f"SatSort - {os.path.basename(file_path)}")
            self.lbl_file_info.setText(f"Açık Dosya: {file_path}")
            self.status_bar.showMessage(f"{len(channels)} {t('T118')} yüklendi.", 4000)
            if channels:
                self.channel_table.selectRow(0)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")

    def save_file(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))  # Liste boş uyarısı
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("T102"),
            self._current_file_path or "channels.sdx",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            write_sdx_file(file_path, channels)
            self._current_file_path = file_path
            self.setWindowTitle(f"SatSort - {os.path.basename(file_path)}")
            self.lbl_file_info.setText(f"Kayıt Yeri: {file_path}")
            QMessageBox.information(self, "SatSort", t("T144"))  # Kayıt tamamlandı
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {e}")

    def toggle_sidebar(self, visible: bool) -> None:
        self.sidebar.setVisible(visible)

    def show_about(self) -> None:
        about_text = (
            "<h3>SatSort v1.0.0</h3>"
            "<p>Linux Native SatcoDX (.sdx) Uydu Kanal Listesi Düzenleyici.</p>"
            "<p><i>Mehmet Taşköprü tarafından geliştirilen NovaSatcoDX projesinden esinlenilerek "
            "Linux platformu için sıfırdan Python ve Qt6 ile geliştirilmiştir.</i></p>"
        )
        QMessageBox.about(self, t("T106"), about_text)

    def _on_language_changed(self, new_lang: str) -> None:
        """Updates all UI text dynamically when language is switched."""
        self._rebuild_language_menu()
        self.channel_table.set_channels(self.channel_table.get_channels())
        self._update_channel_counts()

