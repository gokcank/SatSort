"""
SatSort - Main Window UI
"""

from __future__ import annotations
import os
import shutil
from typing import List, Optional

from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QAction, QKeySequence, QActionGroup, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
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
from ..core.config import config
from ..core.batch_tools import (
    move_radios_to_end,
    remove_scrambled_channels,
    normalize_channel_names,
    remove_duplicate_channels,
)
from ..i18n import i18n, t
from .theme import toggle_theme, get_current_theme
from .channel_table import ChannelTableWidget
from .search_bar import SearchBarWidget
from .sidebar import SidebarWidget
from .dialogs import (
    MovePositionDialog,
    RenameChannelDialog,
    ImportChannelsDialog,
    CompareFilesDialog,
    LanguageSelectionDialog,
    AboutDialog,
)

MATERIAL_SVGS = {
    "folder_open": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>',
    "save": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h11.17L19 7.83V19zm-7-7c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3zM6 6h9v4H6z"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>',
    "delete": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1zM18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z"/></svg>',
    "library_add_check": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12zm-7.53-2.47L18.47 7.53l-1.41-1.41-4.59 4.59-1.59-1.59-1.41 1.41 3 3zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6z"/></svg>',
    "deselect": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>',
    "compare_arrows": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M9.01 14H2v2h7.01v3L13 15.5 9.01 12v2zm5.98-1v-3H22V8h-7.01V5L11 8.5l3.99 3.5z"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M5 20h14v-2H5v2zM19 9h-4V3H9v6H5l7 7 7-7z"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    "arrow_upward": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"/></svg>',
    "arrow_downward": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"/></svg>',
    "exit_to_app": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>',
    "help_outline": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"/></svg>'
}


def _create_material_icon(name: str, color: str = "#38bdf8", size: int = 20) -> QIcon:
    """Creates a crisp, anti-aliased vector QIcon from standard Google Material Symbols SVG."""
    svg_template = MATERIAL_SVGS.get(name, "")
    if not svg_template:
        return QIcon()
    svg_data = svg_template.format(color=color).encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg_data))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    """Main application window for SatSort SatcoDX channel editor."""

    def __init__(self) -> None:
        super().__init__()
        self._current_file_path: Optional[str] = None
        self._all_channels: List[Channel] = []
        self._is_dirty: bool = False
        self._is_loading: bool = False

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
        self.act_open = QAction(_create_material_icon("folder_open", "#38bdf8"), t("T101"), self)
        self.act_open.setShortcut(QKeySequence.Open)
        self.act_open.setToolTip(f"{t('T101')} (Ctrl+O)")
        self.act_open.triggered.connect(self.open_file)
        self.menu_file.addAction(self.act_open)

        # Recent Files Submenu
        self.menu_recent = self.menu_file.addMenu("🕒 " + ("Son Açılan Dosyalar" if i18n.current_language == "Türkçe" else "Recent Files"))
        self._update_recent_files_menu()

        self.act_save = QAction(_create_material_icon("save", "#38bdf8"), "Kaydet" if i18n.current_language == "Türkçe" else "Save", self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.setToolTip(f"{t('T102')} (Ctrl+S)")
        self.act_save.triggered.connect(self.save_file)
        self.menu_file.addAction(self.act_save)

        self.act_close_list = QAction(_create_material_icon("close", "#ef4444"), t("T107"), self)
        self.act_close_list.setShortcut(QKeySequence.Close)
        self.act_close_list.setToolTip(f"{t('T107')} (Ctrl+W)")
        self.act_close_list.triggered.connect(self.close_file)
        self.menu_file.addAction(self.act_close_list)

        self.menu_file.addSeparator()

        self.act_quit = QAction(_create_material_icon("exit_to_app", "#94a3b8"), "Çıkış", self)
        self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_quit.setToolTip("Uygulamadan Çık (Ctrl+Q)")
        self.act_quit.triggered.connect(self.close)
        self.menu_file.addAction(self.act_quit)

        # 2. Edit Menu
        self.menu_edit = menu_bar.addMenu("Düzenle")
        self.act_move_up = QAction(_create_material_icon("arrow_upward", "#38bdf8"), t("T109"), self)
        self.act_move_up.setShortcut("Alt+Up")
        self.act_move_up.setToolTip(f"{t('T109')} (Alt+Up)")
        self.act_move_up.triggered.connect(self.channel_table.move_selected_up)
        self.menu_edit.addAction(self.act_move_up)

        self.act_move_down = QAction(_create_material_icon("arrow_downward", "#38bdf8"), t("T110"), self)
        self.act_move_down.setShortcut("Alt+Down")
        self.act_move_down.setToolTip(f"{t('T110')} (Alt+Down)")
        self.act_move_down.triggered.connect(self.channel_table.move_selected_down)
        self.menu_edit.addAction(self.act_move_down)

        self.act_move_to = QAction("🎯 " + ("Numaraya Taşı..." if i18n.current_language == "Türkçe" else "Move to Slot #..."), self)
        self.act_move_to.setShortcut(QKeySequence("Ctrl+M"))
        self.act_move_to.setToolTip("🎯 " + ("Kanalı Numaraya Taşı (Ctrl+M)" if i18n.current_language == "Türkçe" else "Move Channel to Slot # (Ctrl+M)"))
        self.act_move_to.triggered.connect(lambda: self._on_request_move(is_checked=False))
        self.menu_edit.addAction(self.act_move_to)

        self.menu_edit.addSeparator()

        self.act_del_sel = QAction(_create_material_icon("delete", "#ef4444"), "Seçilenleri Sil" if i18n.current_language == "Türkçe" else "Delete Selected", self)
        self.act_del_sel.setShortcut(QKeySequence.Delete)
        self.act_del_sel.setToolTip(f"{t('T111')} (Delete)")
        self.act_del_sel.triggered.connect(self.channel_table.smart_delete)
        self.menu_edit.addAction(self.act_del_sel)

        self.act_del_chk = QAction(_create_material_icon("delete", "#ef4444"), t("T112"), self)
        self.act_del_chk.setToolTip(t("T112"))
        self.act_del_chk.triggered.connect(self.channel_table.delete_checked)
        self.menu_edit.addAction(self.act_del_chk)

        self.menu_edit.addSeparator()

        self.act_toggle_check = QAction(_create_material_icon("library_add_check", "#38bdf8"), "Tümünü İşaretle" if i18n.current_language == "Türkçe" else "Select All", self)
        self.act_toggle_check.setShortcut(QKeySequence("Ctrl+A"))
        self.act_toggle_check.setToolTip(f"{t('T108')} (Ctrl+A)")
        self.act_toggle_check.triggered.connect(self.channel_table.toggle_all_checked)
        self.menu_edit.addAction(self.act_toggle_check)

        # 3. Tools Menu
        self.menu_tools = menu_bar.addMenu(t("T103"))  # Çoklu İşlemler
        self.act_compare = QAction(_create_material_icon("compare_arrows", "#38bdf8"), "Karşılaştır" if i18n.current_language == "Türkçe" else t("T104"), self)  # Karşılaştırma
        self.act_compare.setShortcut(QKeySequence("Ctrl+K"))
        self.act_compare.setToolTip(f"{t('T104')} (Ctrl+K)")
        self.act_compare.triggered.connect(self._open_compare_dialog)
        self.menu_tools.addAction(self.act_compare)

        self.act_import = QAction(_create_material_icon("download", "#38bdf8"), "İçe Aktar" if i18n.current_language == "Türkçe" else t("T105"), self)  # Farklı Dosyadan Kopyalama
        self.act_import.setShortcut(QKeySequence("Ctrl+I"))
        self.act_import.setToolTip(f"{t('T105')} (Ctrl+I)")
        self.act_import.triggered.connect(self._open_import_dialog)
        self.menu_tools.addAction(self.act_import)

        self.menu_tools.addSeparator()

        is_tr = i18n.current_language == "Türkçe"
        self.act_move_radios_end = QAction("📻 " + ("Radyoları Listenin Sonuna Taşı" if is_tr else "Move Radios to End"), self)
        self.act_move_radios_end.triggered.connect(self._batch_move_radios_to_end)
        self.menu_tools.addAction(self.act_move_radios_end)

        self.act_remove_scrambled = QAction("🔒 " + ("Şifreli Kanalları Sil..." if is_tr else "Remove Scrambled Channels..."), self)
        self.act_remove_scrambled.triggered.connect(self._batch_remove_scrambled)
        self.menu_tools.addAction(self.act_remove_scrambled)

        self.act_normalize_names = QAction("🔤 " + ("Kanal İsimlerini Standartlaştır" if is_tr else "Normalize Channel Names"), self)
        self.act_normalize_names.triggered.connect(self._batch_normalize_names)
        self.menu_tools.addAction(self.act_normalize_names)

        self.act_remove_duplicates = QAction("🔍 " + ("Çift / Mükerrer Kanalları Temizle..." if is_tr else "Remove Duplicate Channels..."), self)
        self.act_remove_duplicates.triggered.connect(self._batch_remove_duplicates)
        self.menu_tools.addAction(self.act_remove_duplicates)

        # 4. Settings Menu
        self.menu_settings = menu_bar.addMenu("Ayarlar" if i18n.current_language == "Türkçe" else "Settings")

        # Theme Submenu
        self.menu_theme = self.menu_settings.addMenu("🎨 Tema" if i18n.current_language == "Türkçe" else "🎨 Theme")
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        current_theme = get_current_theme()

        self.act_dark_theme = QAction("🌙 Koyu Tema" if i18n.current_language == "Türkçe" else "🌙 Dark Theme", self, checkable=True)
        self.act_dark_theme.setChecked(current_theme == "dark")
        self.act_dark_theme.triggered.connect(lambda: self._set_theme("dark"))
        self.theme_action_group.addAction(self.act_dark_theme)
        self.menu_theme.addAction(self.act_dark_theme)

        self.act_light_theme = QAction("☀️ Açık Tema" if i18n.current_language == "Türkçe" else "☀️ Light Theme", self, checkable=True)
        self.act_light_theme.setChecked(current_theme == "light")
        self.act_light_theme.triggered.connect(lambda: self._set_theme("light"))
        self.theme_action_group.addAction(self.act_light_theme)
        self.menu_theme.addAction(self.act_light_theme)

        # Language Submenu
        self.menu_lang = self.menu_settings.addMenu("🌐 " + ("Dil" if i18n.current_language == "Türkçe" else "Language"))
        self._rebuild_language_menu()

        self.menu_settings.addSeparator()

        # Auto-Backup Toggle
        self.act_toggle_auto_backup = QAction("☑️ " + ("Otomatik Yedek Oluştur (.bak)" if i18n.current_language == "Türkçe" else "Create Automatic Backup (.bak)"), self, checkable=True)
        self.act_toggle_auto_backup.setChecked(config.get_auto_backup())
        self.act_toggle_auto_backup.toggled.connect(self._on_toggle_auto_backup)
        self.menu_settings.addAction(self.act_toggle_auto_backup)

        # Sidebar Toggle
        self.act_toggle_sidebar = QAction(_create_material_icon("info", "#3b82f6"), "Bilgi Paneli" if i18n.current_language == "Türkçe" else "Info Panel", self, checkable=True)
        self.act_toggle_sidebar.setChecked(True)
        self.act_toggle_sidebar.setShortcut(QKeySequence("F4"))
        self.act_toggle_sidebar.setToolTip(f"{t('T119')} (F4)")
        self.act_toggle_sidebar.toggled.connect(self.toggle_sidebar)
        self.menu_settings.addAction(self.act_toggle_sidebar)

        # 5. Help Menu
        self.menu_help = menu_bar.addMenu("Yardım" if i18n.current_language == "Türkçe" else "Help")
        self.act_about = QAction(_create_material_icon("help_outline", "#38bdf8"), "ℹ️ " + t("T106"), self)
        self.act_about.setShortcut(QKeySequence("F1"))
        self.act_about.setToolTip(f"{t('T106')} (F1)")
        self.act_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.act_about)

        self.menu_help.addSeparator()

        self.act_report_issue = QAction("🐛 " + ("Hata Bildir / Geri Bildirim" if i18n.current_language == "Türkçe" else "Report Issue / Feedback"), self)
        self.act_report_issue.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort/issues/new")))
        self.menu_help.addAction(self.act_report_issue)

        self.act_github_repo = QAction("⭐ " + ("GitHub Deposu" if i18n.current_language == "Türkçe" else "GitHub Repository"), self)
        self.act_github_repo.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort")))
        self.menu_help.addAction(self.act_github_repo)

        # Top Toolbar (Modern Stitch Vertical Icon-Above-Text Layout)
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setMovable(False)
        self.toolbar.setFixedHeight(48)
        self.addToolBar(self.toolbar)

        # Group 1: File Operations
        self.toolbar.addAction(self.act_open)
        self.toolbar.addAction(self.act_save)
        self.toolbar.addAction(self.act_close_list)
        self.toolbar.addSeparator()

        # Group 2: Delete & Selection
        self.toolbar.addAction(self.act_del_sel)
        self.toolbar.addAction(self.act_toggle_check)
        self.toolbar.addSeparator()

        # Group 3: Advanced Tools
        self.toolbar.addAction(self.act_compare)
        self.toolbar.addAction(self.act_import)
        self.toolbar.addSeparator()

        # Group 4: View Controls
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
        self.channel_table.request_rename.connect(self._on_request_rename)
        self.channel_table.request_move.connect(self._on_request_move)
        self.sidebar.transponder_channel_clicked.connect(self._on_transponder_channel_clicked)
        self.search_bar.text_changed.connect(self._on_search_text_changed)
        self.search_bar.search_confirmed.connect(self._on_search_confirmed)
        self.search_bar.prev_match_requested.connect(self._on_search_prev)
        self.search_bar.next_match_requested.connect(self._on_search_next)
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

    def _on_request_rename(self, row: int, channel: Channel) -> None:
        dlg = RenameChannelDialog(channel.channel_name, self)
        if dlg.exec():
            new_name = dlg.get_channel_name()
            self.channel_table.update_channel_name_at(row, new_name)
            self._set_dirty(True)

    def _on_request_move(self, is_checked: bool = False) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            return
        total = len(channels)

        current_row = 0
        channel_name = None
        if is_checked:
            checked_indices = self.channel_table.get_checked_row_indices()
            if checked_indices:
                current_row = checked_indices[0]
                channel_name = f"{len(checked_indices)} {t('T118')}"
        else:
            sel_indices = self.channel_table.get_selected_row_indices()
            if sel_indices:
                current_row = sel_indices[0]
                channel_name = channels[current_row].channel_name

        is_tr = i18n.current_language == "Türkçe"
        dlg_title = "🎯 " + ("Kanalı Numaraya Taşı" if not is_checked else "İşaretli Kanalları Numaraya Taşı") if is_tr else ("🎯 Move Channel" if not is_checked else "🎯 Move Checked Channels")
        dlg = MovePositionDialog(dlg_title, total, current_row + 1, channel_name, self)
        if dlg.exec():
            target_idx = dlg.get_target_index()

            if is_checked:
                self.channel_table.move_checked_channels(target_idx)
            else:
                self.channel_table.move_channel(current_row, target_idx)
                self.channel_table.selectRow(target_idx)
            self._set_dirty(True)

    def _open_import_dialog(self) -> None:
        dlg = ImportChannelsDialog(self)
        dlg.channels_imported.connect(self._on_channels_imported)
        dlg.exec()

    def _on_channels_imported(self, channels_to_add: List[Channel]) -> None:
        if not channels_to_add:
            return
        current = self.channel_table.get_channels()
        for ch in reversed(channels_to_add):
            ch.is_checked = True
            current.insert(0, ch)
        self.channel_table.set_channels(current)
        self._set_dirty(True)

    def _open_compare_dialog(self) -> None:
        current = self.channel_table.get_channels()
        if not current:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        dlg = CompareDialog(current, self)
        dlg.apply_removals.connect(self._on_apply_removals)
        dlg.apply_additions.connect(self._on_apply_additions)
        dlg.exec()

    def _on_apply_removals(self, channels_to_remove: List[Channel]) -> None:
        current = self.channel_table.get_channels()
        keys_to_remove = {
            (ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate)
            for ch in channels_to_remove
        }
        remaining = [
            ch for ch in current
            if (ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate) not in keys_to_remove
        ]
        self.channel_table.set_channels(remaining)
        self._set_dirty(True)

    def _batch_move_radios_to_end(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        radio_count = sum(1 for c in channels if c.channel_type == "R")
        if radio_count == 0:
            QMessageBox.information(self, "SatSort", "Listede radyo kanalı bulunamadı." if is_tr else "No radio channels found in list.")
            return

        res = QMessageBox.question(
            self,
            "SatSort",
            f"Listede <b>{radio_count}</b> adet radyo kanalı bulundu.<br>Tüm radyolar listenin en sonuna taşınsın mı?" if is_tr
            else f"Found <b>{radio_count}</b> radio channels.<br>Move all radios to the end of the list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if res == QMessageBox.Yes:
            new_channels, moved = move_radios_to_end(channels)
            self.channel_table.set_channels(new_channels)
            self._set_dirty(True)
            self.status_bar.showMessage(f"{moved} radyo kanalı listenin sonuna taşındı." if is_tr else f"{moved} radio channels moved to end.", 4000)

    def _batch_remove_scrambled(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        filtered, removed = remove_scrambled_channels(channels)
        if removed == 0:
            QMessageBox.information(self, "SatSort", "Listede şifreli kanal bulunamadı (Tümü şifresiz/FTA)." if is_tr else "No scrambled channels found in list.")
            return

        res = QMessageBox.question(
            self,
            "SatSort",
            f"Listede <b>{removed}</b> adet şifreli/kriptolu kanal bulundu.<br>Bu kanalların tümü listeden silinsin mi?" if is_tr
            else f"Found <b>{removed}</b> scrambled channels.<br>Remove all scrambled channels from list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if res == QMessageBox.Yes:
            self.channel_table.set_channels(filtered)
            self._set_dirty(True)
            self.status_bar.showMessage(f"{removed} şifreli kanal temizlendi." if is_tr else f"{removed} scrambled channels removed.", 4000)

    def _batch_normalize_names(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        normalized, changed = normalize_channel_names(channels)
        if changed == 0:
            QMessageBox.information(self, "SatSort", "Tüm kanal isimleri zaten standart biçimde." if is_tr else "All channel names are already normalized.")
            return

        res = QMessageBox.question(
            self,
            "SatSort",
            f"<b>{changed}</b> kanalın isminde biçimlendirme / boşluk düzeltmesi tespit edildi.<br>İsimler büyük harf ve standart boşluklarla güncellensin mi?" if is_tr
            else f"Detected formatting/whitespace updates for <b>{changed}</b> channels.<br>Normalize channel names to uppercase standard?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if res == QMessageBox.Yes:
            self.channel_table.set_channels(normalized)
            self._set_dirty(True)
            self.status_bar.showMessage(f"{changed} kanal ismi güncellendi." if is_tr else f"{changed} channel names normalized.", 4000)

    def _batch_remove_duplicates(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        deduped, dup_count = remove_duplicate_channels(channels)
        if dup_count == 0:
            QMessageBox.information(self, "SatSort", "Listede çift / mükerrer kanal bulunamadı." if is_tr else "No duplicate channels found in list.")
            return

        res = QMessageBox.question(
            self,
            "SatSort",
            f"Listede <b>{dup_count}</b> adet mükerrer (çift) kanal bulundu.<br>İlk kopyalar korunarak fazlalıklar silinsin mi?" if is_tr
            else f"Found <b>{dup_count}</b> duplicate channels.<br>Remove duplicate entries while keeping the first occurrence?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if res == QMessageBox.Yes:
            self.channel_table.set_channels(deduped)
            self._set_dirty(True)
            self.status_bar.showMessage(f"{dup_count} mükerrer kanal silindi." if is_tr else f"{dup_count} duplicate channels removed.", 4000)

    def _on_apply_additions(self, channels_to_add: List[Channel]) -> None:
        if not channels_to_add:
            return
        current = self.channel_table.get_channels()
        for ch in reversed(channels_to_add):
            ch.is_checked = True
            current.insert(0, ch)
        self.channel_table.set_channels(current)
        self._set_dirty(True)

    def _set_dirty(self, dirty: bool = True) -> None:
        self._is_dirty = dirty
        self._update_window_title()

    def _update_window_title(self) -> None:
        dirty_mark = " *" if self._is_dirty else ""
        if self._current_file_path:
            base = os.path.basename(self._current_file_path)
            self.setWindowTitle(f"SatSort - {base}{dirty_mark}")
        else:
            self.setWindowTitle(f"SatSort - SatcoDX Channel Editor{dirty_mark}")

    def _update_channel_counts(self) -> None:
        channels = self.channel_table.get_channels()
        checked_count = len([ch for ch in channels if ch.is_checked])
        self.lbl_channel_count.setText(f"{t('T118')}: {len(channels)} | İşaretli: {checked_count}")
        selected_ch = self.channel_table.get_selected_channel()
        if selected_ch:
            self.sidebar.set_channel(selected_ch, channels)

        # Synchronize toggle check all / uncheck all action state
        if hasattr(self, "act_toggle_check"):
            if channels and checked_count == len(channels):
                self.act_toggle_check.setText(t("T108"))  # İşaretleri Kaldır
                self.act_toggle_check.setToolTip(f"{t('T108')} (Ctrl+A)")
                self.act_toggle_check.setIcon(_create_material_icon("deselect", "#94a3b8"))
            else:
                check_label = "Tümünü İşaretle" if i18n.current_language == "Türkçe" else ("Select All" if i18n.current_language == "English" else ("Alle auswählen" if i18n.current_language == "Deutsch" else "Tout sélectionner"))
                self.act_toggle_check.setText(check_label)
                self.act_toggle_check.setToolTip(f"{check_label} (Ctrl+A)")
                self.act_toggle_check.setIcon(_create_material_icon("library_add_check", "#38bdf8"))

        if hasattr(self, "search_bar"):
            self.search_bar.set_has_channels(len(channels) > 0)

        if not self._is_loading and (self._current_file_path is not None or len(channels) > 0):
            self._set_dirty(True)

    def _on_search_text_changed(self, text: str) -> None:
        matches = self.channel_table.search_channels(text)
        self.search_bar.set_match_status(
            self.channel_table.get_current_match_index(),
            len(matches),
            len(self.channel_table.get_channels()),
        )

    def _on_search_prev(self) -> None:
        if self.search_bar.get_text():
            idx = self.channel_table.goto_prev_match()
            self.search_bar.set_match_status(
                idx,
                len(self.channel_table.get_search_matches()),
                len(self.channel_table.get_channels()),
            )
        else:
            self.channel_table.move_selected_up()

    def _on_search_next(self) -> None:
        if self.search_bar.get_text():
            idx = self.channel_table.goto_next_match()
            self.search_bar.set_match_status(
                idx,
                len(self.channel_table.get_search_matches()),
                len(self.channel_table.get_channels()),
            )
        else:
            self.channel_table.move_selected_down()

    def _on_search_confirmed(self, text: str) -> None:
        if text:
            match_count = self.channel_table.mark_matching_channels(text)
            self.search_bar.set_match_status(
                self.channel_table.get_current_match_index(),
                match_count,
                len(self.channel_table.get_channels()),
            )

            if match_count == 0:
                self.status_bar.showMessage(t("T142"), 4000)  # Kanal bulunamadı
            else:
                self.status_bar.showMessage(f"{match_count} {t('T143')}", 4000)  # X Kanal bulundu ve işaretlendi
        else:
            self.channel_table.toggle_all_checked()

    def _on_search_cleared(self) -> None:
        self.channel_table.clear_search_matches()
        self.search_bar.set_match_status(-1, 0, len(self.channel_table.get_channels()))

    def _maybe_save_changes(self) -> bool:
        """
        Prompts the user to save changes if unsaved modifications exist.
        Returns True if safe to proceed (saved or discarded), False if cancelled.
        """
        if not self._is_dirty:
            return True

        reply = QMessageBox.question(
            self,
            "SatSort",
            "Kaydedilmemiş değişiklikleriniz var. Değişiklikleri kaydetmek istiyor musunuz?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )

        if reply == QMessageBox.Save:
            return self.save_file()
        elif reply == QMessageBox.Discard:
            return True
        else:  # QMessageBox.Cancel
            return False

    def load_file_path(self, file_path: str) -> bool:
        """Loads a .sdx file directly by path with error handling and recent files update."""
        if not os.path.exists(file_path):
            is_tr = i18n.current_language == "Türkçe"
            QMessageBox.warning(self, "SatSort", f"Dosya bulunamadı:\n{file_path}" if is_tr else f"File not found:\n{file_path}")
            config.remove_recent_file(file_path)
            self._update_recent_files_menu()
            return False

        try:
            self._is_loading = True
            channels = read_sdx_file(file_path)
            self._current_file_path = file_path
            self._all_channels = channels
            self.channel_table.set_channels(channels)
            self._is_loading = False
            self._set_dirty(False)
            self.lbl_file_info.setText(f"Açık Dosya: {file_path}")
            self.status_bar.showMessage(f"{len(channels)} {t('T118')} yüklendi.", 4000)
            if channels:
                self.channel_table.selectRow(0)

            config.add_recent_file(file_path)
            self._update_recent_files_menu()
            return True
        except Exception as e:
            self._is_loading = False
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")
            return False

    def _update_recent_files_menu(self) -> None:
        """Dynamically populates the Recent Files submenu."""
        self.menu_recent.clear()
        recent_files = config.get_recent_files()
        is_tr = i18n.current_language == "Türkçe"

        if not recent_files:
            act_empty = QAction("Boş" if is_tr else "Empty", self)
            act_empty.setEnabled(False)
            self.menu_recent.addAction(act_empty)
            return

        for i, path in enumerate(recent_files):
            basename = os.path.basename(path)
            act = QAction(f"{i + 1}. {basename}", self)
            act.setToolTip(path)
            act.triggered.connect(lambda checked=False, p=path: self._on_open_recent(p))
            self.menu_recent.addAction(act)

        self.menu_recent.addSeparator()
        act_clear = QAction("🗑️ " + ("Listeyi Temizle" if is_tr else "Clear List"), self)
        act_clear.triggered.connect(self._clear_recent_files)
        self.menu_recent.addAction(act_clear)

    def _on_open_recent(self, path: str) -> None:
        """Opens a file selected from the Recent Files menu after prompting for dirty state."""
        if not self._maybe_save_changes():
            return
        self.load_file_path(path)

    def _clear_recent_files(self) -> None:
        """Clears recent files list from persistent config and updates menu."""
        config.clear_recent_files()
        self._update_recent_files_menu()

    def _on_toggle_auto_backup(self, checked: bool) -> None:
        """Saves auto-backup preference to persistent configuration."""
        config.set_auto_backup(checked)

    def open_file(self) -> bool:
        if not self._maybe_save_changes():
            return False

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("T101"),
            "",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return False

        return self.load_file_path(file_path)

    def save_file(self) -> bool:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))  # Liste boş uyarısı
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("T102"),
            self._current_file_path or "channels.sdx",
            "SatcoDx Files (*.sdx);;All Files (*.*)",
        )
        if not file_path:
            return False

        try:
            # Create automatic safety backup (.bak) if file already exists and auto-backup is enabled
            if os.path.exists(file_path) and config.get_auto_backup():
                bak_path = f"{file_path}.bak"
                try:
                    shutil.copy2(file_path, bak_path)
                except Exception:
                    pass

            write_sdx_file(file_path, channels)
            self._current_file_path = file_path
            self._set_dirty(False)
            self.lbl_file_info.setText(f"Kayıt Yeri: {file_path}")
            config.add_recent_file(file_path)
            self._update_recent_files_menu()
            QMessageBox.information(self, "SatSort", t("T144"))  # Kayıt tamamlandı
            return True
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {e}")
            return False

    def close_file(self) -> bool:
        """Closes the current channel list, clears table and resets window to ready state."""
        if not self._maybe_save_changes():
            return False

        self._current_file_path = None
        self._all_channels = []
        self.channel_table.set_channels([])
        self.sidebar.clear()
        self.search_bar.clear()
        self._set_dirty(False)
        self.lbl_file_info.setText("Hazır")
        self.status_bar.showMessage("Kanal listesi kapatıldı.", 3000)
        return True

    def closeEvent(self, event) -> None:
        if self._maybe_save_changes():
            event.accept()
        else:
            event.ignore()

    def toggle_sidebar(self, visible: bool) -> None:
        self.sidebar.setVisible(visible)

    def _set_theme(self, theme_name: str) -> None:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            from .theme import apply_theme
            apply_theme(app, theme_name)
            self.act_dark_theme.setChecked(theme_name == "dark")
            self.act_light_theme.setChecked(theme_name == "light")
            # Refresh channel table row backgrounds
            self.channel_table.set_channels(self.channel_table.get_channels())

    def show_about(self) -> None:
        AboutDialog(self).exec()

    def retranslate_ui(self) -> None:
        """Dynamically retranslates all menus, actions, tooltips, tables and subcomponents."""
        self._update_window_title()

        # Menus
        self.menu_file.setTitle(t("T100"))
        self.menu_recent.setTitle("🕒 " + ("Son Açılan Dosyalar" if i18n.current_language == "Türkçe" else "Recent Files"))
        self._update_recent_files_menu()
        self.menu_edit.setTitle("Düzenle" if i18n.current_language == "Türkçe" else ("Edit" if i18n.current_language == "English" else ("Bearbeiten" if i18n.current_language == "Deutsch" else "Éditer")))
        self.menu_tools.setTitle(t("T103"))
        self.menu_settings.setTitle("Ayarlar" if i18n.current_language == "Türkçe" else ("Settings" if i18n.current_language == "English" else ("Einstellungen" if i18n.current_language == "Deutsch" else "Paramètres")))
        self.menu_theme.setTitle("🎨 " + ("Tema" if i18n.current_language == "Türkçe" else ("Theme" if i18n.current_language == "English" else "Theme")))
        self.menu_lang.setTitle("🌐 " + ("Dil" if i18n.current_language == "Türkçe" else ("Language" if i18n.current_language == "English" else "Sprache")))
        self.menu_help.setTitle("Yardım" if i18n.current_language == "Türkçe" else ("Help" if i18n.current_language == "English" else ("Hilfe" if i18n.current_language == "Deutsch" else "Aide")))

        # Theme actions
        self.act_dark_theme.setText("🌙 " + ("Koyu Tema" if i18n.current_language == "Türkçe" else "Dark Theme"))
        self.act_light_theme.setText("☀️ " + ("Açık Tema" if i18n.current_language == "Türkçe" else "Light Theme"))
        self.act_toggle_auto_backup.setText("☑️ " + ("Otomatik Yedek Oluştur (.bak)" if i18n.current_language == "Türkçe" else "Create Automatic Backup (.bak)"))

        # File actions
        self.act_open.setText(t("T101"))
        self.act_open.setToolTip(f"{t('T101')} (Ctrl+O)")

        self.act_save.setText(t("T102"))
        self.act_save.setToolTip(f"{t('T102')} (Ctrl+S)")

        self.act_close_list.setText(t("T127"))
        self.act_close_list.setToolTip(f"{t('T127')} (Ctrl+W)")

        self.act_quit.setText("Çıkış" if i18n.current_language == "Türkçe" else ("Quit" if i18n.current_language == "English" else ("Beenden" if i18n.current_language == "Deutsch" else "Quitter")))
        self.act_quit.setToolTip("Uygulamadan Çık (Ctrl+Q)")

        # Edit actions
        self.act_move_up.setText(t("T109"))
        self.act_move_up.setToolTip(f"{t('T109')} (Alt+Up)")

        self.act_move_down.setText(t("T110"))
        self.act_move_down.setToolTip(f"{t('T110')} (Alt+Down)")

        self.act_move_to.setText("🎯 " + ("Numaraya Taşı..." if i18n.current_language == "Türkçe" else "Move to Slot #..."))
        self.act_move_to.setToolTip("🎯 " + ("Kanalı Numaraya Taşı (Ctrl+M)" if i18n.current_language == "Türkçe" else "Move Channel to Slot # (Ctrl+M)"))

        self.act_del_sel.setText(t("T111"))
        self.act_del_sel.setToolTip(f"{t('T111')} (Delete)")

        self.act_del_chk.setText(t("T112"))
        self.act_del_chk.setToolTip(t("T112"))

        self.act_compare.setText(t("T104"))
        self.act_compare.setToolTip(f"{t('T104')} (Ctrl+K)")

        self.act_import.setText(t("T105"))
        self.act_import.setToolTip(f"{t('T105')} (Ctrl+I)")

        is_tr = i18n.current_language == "Türkçe"
        self.act_move_radios_end.setText("📻 " + ("Radyoları Listenin Sonuna Taşı" if is_tr else "Move Radios to End"))
        self.act_remove_scrambled.setText("🔒 " + ("Şifreli Kanalları Sil..." if is_tr else "Remove Scrambled Channels..."))
        self.act_normalize_names.setText("🔤 " + ("Kanal İsimlerini Standartlaştır" if is_tr else "Normalize Channel Names"))
        self.act_remove_duplicates.setText("🔍 " + ("Çift / Mükerrer Kanalları Temizle..." if is_tr else "Remove Duplicate Channels..."))

        self.act_toggle_sidebar.setText(t("T119"))
        self.act_toggle_sidebar.setToolTip(f"{t('T119')} (F4)")

        self.act_about.setText(t("T106"))
        self.act_about.setToolTip(f"{t('T106')} (F1)")

        self.act_report_issue.setText("🐛 " + ("Hata Bildir / Geri Bildirim" if i18n.current_language == "Türkçe" else "Report Issue / Feedback"))
        self.act_github_repo.setText("⭐ " + ("GitHub Deposu" if i18n.current_language == "Türkçe" else "GitHub Repository"))

        # Subcomponents
        self._rebuild_language_menu()
        self.search_bar.retranslate_ui()
        self.channel_table.retranslate_ui()
        self.sidebar.retranslate_ui()
        self._update_channel_counts()

    def _on_language_changed(self, new_lang: str) -> None:
        """Updates all UI text dynamically when language is switched."""
        self.retranslate_ui()

