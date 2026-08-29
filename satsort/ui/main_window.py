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
    QToolButton,
    QMenu,
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
from ..core.exporter import export_to_csv, export_to_txt, export_to_m3u
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
    ReferenceSortDialog,
    ShortcutsDialog,
)

from .icons import get_icon


def _create_material_icon(name: str, color: Optional[str] = None, size: int = 20) -> QIcon:
    """Creates a crisp, anti-aliased vector QIcon from Google Material Symbols SVG."""
    return get_icon(name, color=color, size=size)


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
        self.menu_recent = self.menu_file.addMenu(get_icon("history"), "Son Açılan Dosyalar" if i18n.current_language == "Türkçe" else "Recent Files")
        self._update_recent_files_menu()

        self.act_save = QAction(_create_material_icon("save", "#38bdf8"), "Kaydet" if i18n.current_language == "Türkçe" else "Save", self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.setToolTip(f"{t('T102')} (Ctrl+S)")
        self.act_save.triggered.connect(self.save_file)
        self.menu_file.addAction(self.act_save)

        # Export Submenu
        is_tr = i18n.current_language == "Türkçe"
        self.menu_export = self.menu_file.addMenu(get_icon("download"), "Dışa Aktar" if is_tr else "Export")
        self.act_export_csv = QAction(get_icon("description"), "CSV Dosyası Olarak (.csv)..." if is_tr else "As CSV File (.csv)...", self)
        self.act_export_csv.triggered.connect(self._export_csv)
        self.menu_export.addAction(self.act_export_csv)

        self.act_export_txt = QAction(get_icon("text_snippet"), "Metin Dosyası Olarak (.txt)..." if is_tr else "As Text File (.txt)...", self)
        self.act_export_txt.triggered.connect(self._export_txt)
        self.menu_export.addAction(self.act_export_txt)

        self.act_export_m3u = QAction(get_icon("playlist_play"), "M3U Listesi Olarak (.m3u)..." if is_tr else "As M3U Playlist (.m3u)...", self)
        self.act_export_m3u.triggered.connect(self._export_m3u)
        self.menu_export.addAction(self.act_export_m3u)

        self.menu_file.addSeparator()

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

        self.act_move_to = QAction(get_icon("near_me"), "Numaraya Taşı..." if i18n.current_language == "Türkçe" else "Move to Slot #...", self)
        self.act_move_to.setShortcut(QKeySequence("Ctrl+M"))
        self.act_move_to.setToolTip(f"{'Kanalı Numaraya Taşı' if i18n.current_language == 'Türkçe' else 'Move Channel to Slot #'} (Ctrl+M)")
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

        # 3. View Menu (Görünüm Menüsü)
        self.menu_view = menu_bar.addMenu("Görünüm" if is_tr else "View")

        # Sidebar Toggle
        self.act_toggle_sidebar = QAction(_create_material_icon("info", "#3b82f6"), "Bilgi Paneli" if is_tr else "Info Panel", self, checkable=True)
        self.act_toggle_sidebar.setChecked(True)
        self.act_toggle_sidebar.setShortcut(QKeySequence("F4"))
        self.act_toggle_sidebar.setToolTip(f"{t('T119')} (F4)")
        self.act_toggle_sidebar.toggled.connect(self.toggle_sidebar)
        self.menu_view.addAction(self.act_toggle_sidebar)

        self.menu_view.addSeparator()

        # Theme Submenu
        self.menu_theme = self.menu_view.addMenu(get_icon("dark_mode"), "Tema" if is_tr else "Theme")
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        current_theme = get_current_theme()

        self.act_dark_theme = QAction(get_icon("dark_mode"), "Koyu Tema" if is_tr else "Dark Theme", self, checkable=True)
        self.act_dark_theme.setChecked(current_theme == "dark")
        self.act_dark_theme.triggered.connect(lambda: self._set_theme("dark"))
        self.theme_action_group.addAction(self.act_dark_theme)
        self.menu_theme.addAction(self.act_dark_theme)

        self.act_light_theme = QAction(get_icon("light_mode", "#f59e0b"), "Açık Tema" if is_tr else "Light Theme", self, checkable=True)
        self.act_light_theme.setChecked(current_theme == "light")
        self.act_light_theme.triggered.connect(lambda: self._set_theme("light"))
        self.theme_action_group.addAction(self.act_light_theme)
        self.menu_theme.addAction(self.act_light_theme)

        # Toolbar Appearance Submenu
        self.menu_toolbar_style = self.menu_view.addMenu(get_icon("view_agenda"), "Araç Çubuğu Görünümü" if is_tr else "Toolbar Appearance")
        self.tb_style_group = QActionGroup(self)
        self.tb_style_group.setExclusive(True)

        self.act_tb_text_under = QAction("İkon Altında Metin" if is_tr else "Text Under Icons", self, checkable=True)
        self.act_tb_text_under.triggered.connect(lambda: self._set_toolbar_style("text_under_icon"))
        self.tb_style_group.addAction(self.act_tb_text_under)
        self.menu_toolbar_style.addAction(self.act_tb_text_under)

        self.act_tb_text_beside = QAction("İkon Yanında Metin" if is_tr else "Text Beside Icons", self, checkable=True)
        self.act_tb_text_beside.triggered.connect(lambda: self._set_toolbar_style("text_beside_icon"))
        self.tb_style_group.addAction(self.act_tb_text_beside)
        self.menu_toolbar_style.addAction(self.act_tb_text_beside)

        self.act_tb_icon_only = QAction("Yalnızca İkon (Kompakt)" if is_tr else "Icons Only (Compact)", self, checkable=True)
        self.act_tb_icon_only.triggered.connect(lambda: self._set_toolbar_style("icon_only"))
        self.tb_style_group.addAction(self.act_tb_icon_only)
        self.menu_toolbar_style.addAction(self.act_tb_icon_only)

        # 4. Tools Menu (Çoklu İşlemler)
        self.menu_tools = menu_bar.addMenu(t("T103"))  # Çoklu İşlemler

        # Group A: Inter-File Operations (Dosyalar Arası İşlemler)
        self.act_compare = QAction(_create_material_icon("compare_arrows", "#38bdf8"), "Karşılaştır" if is_tr else t("T104"), self)
        self.act_compare.setShortcut(QKeySequence("Ctrl+K"))
        self.act_compare.setToolTip(f"{t('T104')} (Ctrl+K)")
        self.act_compare.triggered.connect(self._open_compare_dialog)
        self.menu_tools.addAction(self.act_compare)

        self.act_import = QAction(_create_material_icon("download", "#38bdf8"), "İçe Aktar" if is_tr else t("T105"), self)
        self.act_import.setShortcut(QKeySequence("Ctrl+I"))
        self.act_import.setToolTip(f"{t('T105')} (Ctrl+I)")
        self.act_import.triggered.connect(self._open_import_dialog)
        self.menu_tools.addAction(self.act_import)

        self.act_ref_sort = QAction(get_icon("link"), "Referans Liste ile Sırala..." if is_tr else "Sort by Reference List...", self)
        self.act_ref_sort.triggered.connect(self._open_reference_sort_dialog)
        self.menu_tools.addAction(self.act_ref_sort)

        self.menu_tools.addSeparator()

        # Group B: Batch Cleanup & Standardization (Toplu Liste Temizliği & Düzenleme)
        self.act_normalize_names = QAction(get_icon("spellcheck"), "Kanal İsimlerini Standartlaştır" if is_tr else "Normalize Channel Names", self)
        self.act_normalize_names.triggered.connect(self._batch_normalize_names)
        self.menu_tools.addAction(self.act_normalize_names)

        self.act_remove_scrambled = QAction(get_icon("lock", "#ef4444"), "Şifreli Kanalları Sil..." if is_tr else "Remove Scrambled Channels...", self)
        self.act_remove_scrambled.triggered.connect(self._batch_remove_scrambled)
        self.menu_tools.addAction(self.act_remove_scrambled)

        self.act_remove_duplicates = QAction(get_icon("filter_alt"), "Çift / Mükerrer Kanalları Temizle..." if is_tr else "Remove Duplicate Channels...", self)
        self.act_remove_duplicates.triggered.connect(self._batch_remove_duplicates)
        self.menu_tools.addAction(self.act_remove_duplicates)

        self.act_move_radios_end = QAction(get_icon("radio"), "Radyoları Listenin Sonuna Taşı" if is_tr else "Move Radios to End", self)
        self.act_move_radios_end.triggered.connect(self._batch_move_radios_to_end)
        self.menu_tools.addAction(self.act_move_radios_end)

        # 5. Settings Menu (Sadeleştirilmiş Ayarlar)
        self.menu_settings = menu_bar.addMenu("Ayarlar" if is_tr else "Settings")

        # Language Submenu
        self.menu_lang = self.menu_settings.addMenu(get_icon("language"), "Dil" if is_tr else "Language")
        self._rebuild_language_menu()

        self.menu_settings.addSeparator()

        # Auto-Backup Toggle
        self.act_toggle_auto_backup = QAction(get_icon("backup"), "Otomatik Yedek Oluştur (.bak)" if is_tr else "Create Automatic Backup (.bak)", self, checkable=True)
        self.act_toggle_auto_backup.setChecked(config.get_auto_backup())
        self.act_toggle_auto_backup.toggled.connect(self._on_toggle_auto_backup)
        self.menu_settings.addAction(self.act_toggle_auto_backup)

        # 6. Help Menu
        self.menu_help = menu_bar.addMenu("Yardım" if is_tr else "Help")
        self.act_about = QAction(_create_material_icon("help_outline", "#38bdf8"), t("T106"), self)
        self.act_about.setShortcut(QKeySequence("F1"))
        self.act_about.setToolTip(f"{t('T106')} (F1)")
        self.act_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.act_about)

        self.act_shortcuts = QAction(get_icon("keyboard"), "Klavye Kısayolları" if is_tr else "Keyboard Shortcuts", self)
        self.act_shortcuts.setShortcut(QKeySequence("Ctrl+/"))
        self.act_shortcuts.setToolTip(f"{'Klavye Kısayolları' if is_tr else 'Keyboard Shortcuts'} (Ctrl+/)")
        self.act_shortcuts.triggered.connect(self._open_shortcuts_dialog)
        self.menu_help.addAction(self.act_shortcuts)

        self.menu_help.addSeparator()

        self.act_report_issue = QAction(get_icon("bug_report", "#ef4444"), "Hata Bildir / Geri Bildirim" if is_tr else "Report Issue / Feedback", self)
        self.act_report_issue.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort/issues/new")))
        self.menu_help.addAction(self.act_report_issue)

        self.act_github_repo = QAction(get_icon("star", "#f59e0b"), "GitHub Deposu" if is_tr else "GitHub Repository", self)
        self.act_github_repo.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort")))
        self.menu_help.addAction(self.act_github_repo)

        self.menu_help.addSeparator()

        self.act_check_updates = QAction(get_icon("update", "#10b981"), "Güncellemeleri Denetle..." if is_tr else "Check for Updates...", self)
        self.act_check_updates.triggered.connect(self._check_for_updates)
        self.menu_help.addAction(self.act_check_updates)

        # Top Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self._set_toolbar_style(config.get_toolbar_style())

        # Group 1: File Operations
        self.toolbar.addAction(self.act_open)
        self.toolbar.addAction(self.act_save)
        self.toolbar.addSeparator()

        # Group 2: Channel Movement & Reordering (Numaraya Taşı, Yukarı, Aşağı)
        self.toolbar.addAction(self.act_move_to)
        self.toolbar.addAction(self.act_move_up)
        self.toolbar.addAction(self.act_move_down)
        self.toolbar.addSeparator()

        # Group 3: Delete & Selection
        self.toolbar.addAction(self.act_del_sel)
        self.toolbar.addAction(self.act_toggle_check)
        self.toolbar.addSeparator()

        # Group 4: Analysis & View
        self.toolbar.addAction(self.act_compare)
        self.toolbar.addAction(self.act_toggle_sidebar)

    def _rebuild_language_menu(self) -> None:
        self.menu_lang.clear()
        for lang in i18n.get_supported_languages():
            endonym = i18n.get_language_endonym(lang)
            code = i18n.get_language_code(lang)
            act = QAction(f"{endonym} ({code})", self, checkable=True)
            act.setChecked(lang == i18n.current_language)
            act.triggered.connect(lambda checked, l=lang: i18n.set_language(l))
            self.menu_lang.addAction(act)

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_file_info = QLabel("Hazır")
        self.lbl_channel_count = QLabel("Kanal: 0 | İşaretli: 0")

        # Quick Language Selector Button in Status Bar
        self.btn_lang = QToolButton()
        self.btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setToolTip("Dil Seçimi / Select Language")
        self.btn_lang.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
                color: #38bdf8;
                margin-left: 6px;
            }
            QToolButton:hover {
                background-color: #1e293b;
                border-color: #38bdf8;
            }
            QToolButton::menu-indicator {
                image: none;
                width: 0px;
            }
        """)
        self.status_lang_menu = QMenu(self)
        self.btn_lang.setMenu(self.status_lang_menu)
        self._update_status_lang_button()

        self.status_bar.addWidget(self.lbl_file_info, stretch=1)
        self.status_bar.addPermanentWidget(self.lbl_channel_count)
        self.status_bar.addPermanentWidget(self.btn_lang)

    def _update_status_lang_button(self) -> None:
        """Updates the status bar language button text and its popup menu."""
        code = i18n.get_language_code()
        self.btn_lang.setIcon(get_icon("language"))
        self.btn_lang.setText(f"{code} ▾")
        self.status_lang_menu.clear()
        for lang in i18n.get_supported_languages():
            endonym = i18n.get_language_endonym(lang)
            c = i18n.get_language_code(lang)
            act = QAction(f"{endonym} ({c})", self, checkable=True)
            act.setChecked(lang == i18n.current_language)
            act.triggered.connect(lambda checked, l=lang: i18n.set_language(l))
            self.status_lang_menu.addAction(act)

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
        dlg_title = ("Kanalı Numaraya Taşı" if not is_checked else "İşaretli Kanalları Numaraya Taşı") if is_tr else ("Move Channel" if not is_checked else "Move Checked Channels")
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

    def _open_reference_sort_dialog(self) -> None:
        current = self.channel_table.get_channels()
        if not current:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        dlg = ReferenceSortDialog(current, self)
        dlg.sorting_applied.connect(self._on_reference_sorting_applied)
        dlg.exec()

    def _on_reference_sorting_applied(self, sorted_channels: List[Channel]) -> None:
        self.channel_table.set_channels(sorted_channels)
        self._set_dirty(True)
        is_tr = i18n.current_language == "Türkçe"
        self.status_bar.showMessage("Referans sıralama başarıyla uygulandı." if is_tr else "Reference sorting applied successfully.", 4000)

    def _export_csv(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSV Olarak Dışa Aktar" if is_tr else "Export to CSV",
            "channels.csv",
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if file_path:
            try:
                export_to_csv(channels, file_path)
                self.status_bar.showMessage(f"CSV başarıyla kaydedildi: {file_path}" if is_tr else f"Exported CSV: {file_path}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {e}")

    def _export_txt(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Metin Dosyası Olarak Dışa Aktar" if is_tr else "Export to Text File",
            "channels.txt",
            "Text Files (*.txt);;All Files (*.*)",
        )
        if file_path:
            try:
                export_to_txt(channels, file_path)
                self.status_bar.showMessage(f"Metin listesi başarıyla kaydedildi: {file_path}" if is_tr else f"Exported TXT: {file_path}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {e}")

    def _export_m3u(self) -> None:
        channels = self.channel_table.get_channels()
        if not channels:
            QMessageBox.warning(self, "SatSort", t("T145"))
            return

        is_tr = i18n.current_language == "Türkçe"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "M3U Oynatma Listesi Olarak Dışa Aktar" if is_tr else "Export to M3U Playlist",
            "channels.m3u",
            "M3U Playlists (*.m3u *.m3u8);;All Files (*.*)",
        )
        if file_path:
            try:
                export_to_m3u(channels, file_path)
                self.status_bar.showMessage(f"M3U listesi başarıyla kaydedildi: {file_path}" if is_tr else f"Exported M3U: {file_path}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {e}")

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
        act_clear = QAction(get_icon("delete_sweep", "#ef4444"), "Listeyi Temizle" if is_tr else "Clear List", self)
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
            # Refresh channel table row backgrounds and badges
            self.channel_table.set_channels(self.channel_table.get_channels())
            # Refresh sidebar transponder list
            selected = self.channel_table.get_selected_channel()
            self.sidebar.set_channel(selected, self.channel_table.get_channels())

    def _set_toolbar_style(self, style_name: str) -> None:
        """Configures toolbar display mode between text_under_icon, text_beside_icon, and icon_only."""
        if style_name == "icon_only":
            self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
            self.toolbar.setFixedHeight(36)
            self.act_tb_icon_only.setChecked(True)
        elif style_name == "text_beside_icon":
            self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.toolbar.setFixedHeight(36)
            self.act_tb_text_beside.setChecked(True)
        else:
            self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.toolbar.setFixedHeight(48)
            self.act_tb_text_under.setChecked(True)
            style_name = "text_under_icon"

        config.set_toolbar_style(style_name)

    def show_about(self) -> None:
        AboutDialog(self).exec()

    def _check_for_updates(self) -> None:
        from .dialogs.update_dialog import UpdateDialog
        UpdateDialog(self).exec()

    def _open_shortcuts_dialog(self) -> None:
        ShortcutsDialog(self).exec()

    def retranslate_ui(self) -> None:
        """Dynamically retranslates all menus, actions, tooltips, tables and subcomponents."""
        self._update_window_title()

        # Menus
        self.menu_file.setTitle(t("T100"))
        self.menu_recent.setTitle("Son Açılan Dosyalar" if i18n.current_language == "Türkçe" else "Recent Files")
        self._update_recent_files_menu()
        self.menu_edit.setTitle("Düzenle" if i18n.current_language == "Türkçe" else ("Edit" if i18n.current_language == "English" else ("Bearbeiten" if i18n.current_language == "Deutsch" else "Éditer")))
        self.menu_view.setTitle("Görünüm" if i18n.current_language == "Türkçe" else ("View" if i18n.current_language == "English" else ("Ansicht" if i18n.current_language == "Deutsch" else "Affichage")))
        self.menu_tools.setTitle(t("T103"))
        self.menu_settings.setTitle("Ayarlar" if i18n.current_language == "Türkçe" else ("Settings" if i18n.current_language == "English" else ("Einstellungen" if i18n.current_language == "Deutsch" else "Paramètres")))
        self.menu_theme.setTitle("Tema" if i18n.current_language == "Türkçe" else ("Theme" if i18n.current_language == "English" else "Theme"))
        self.menu_lang.setTitle("Dil" if i18n.current_language == "Türkçe" else ("Language" if i18n.current_language == "English" else "Sprache"))
        self.menu_help.setTitle("Yardım" if i18n.current_language == "Türkçe" else ("Help" if i18n.current_language == "English" else ("Hilfe" if i18n.current_language == "Deutsch" else "Aide")))

        is_tr = i18n.current_language == "Türkçe"
        self.menu_toolbar_style.setTitle("Araç Çubuğu Görünümü" if is_tr else "Toolbar Appearance")
        self.act_tb_text_under.setText("İkon Altında Metin" if is_tr else "Text Under Icons")
        self.act_tb_text_beside.setText("İkon Yanında Metin" if is_tr else "Text Beside Icons")
        self.act_tb_icon_only.setText("Yalnızca İkon (Kompakt)" if is_tr else "Icons Only (Compact)")

        # Theme actions
        self.act_dark_theme.setText("Koyu Tema" if i18n.current_language == "Türkçe" else "Dark Theme")
        self.act_light_theme.setText("Açık Tema" if i18n.current_language == "Türkçe" else "Light Theme")
        self.act_toggle_auto_backup.setText("Otomatik Yedek Oluştur (.bak)" if i18n.current_language == "Türkçe" else "Create Automatic Backup (.bak)")

        # File actions
        self.act_open.setText(t("T101"))
        self.act_open.setToolTip(f"{t('T101')} (Ctrl+O)")

        self.act_save.setText(t("T102"))
        self.act_save.setToolTip(f"{t('T102')} (Ctrl+S)")

        self.menu_export.setTitle("Dışa Aktar" if is_tr else "Export")
        self.act_export_csv.setText("CSV Dosyası Olarak (.csv)..." if is_tr else "As CSV File (.csv)...")
        self.act_export_txt.setText("Metin Dosyası Olarak (.txt)..." if is_tr else "As Text File (.txt)...")
        self.act_export_m3u.setText("M3U Listesi Olarak (.m3u)..." if is_tr else "As M3U Playlist (.m3u)...")

        self.act_close_list.setText(t("T127"))
        self.act_close_list.setToolTip(f"{t('T127')} (Ctrl+W)")

        self.act_quit.setText("Çıkış" if i18n.current_language == "Türkçe" else ("Quit" if i18n.current_language == "English" else ("Beenden" if i18n.current_language == "Deutsch" else "Quitter")))
        self.act_quit.setToolTip("Uygulamadan Çık (Ctrl+Q)")

        # Edit actions
        self.act_move_up.setText(t("T109"))
        self.act_move_up.setToolTip(f"{t('T109')} (Alt+Up)")

        self.act_move_down.setText(t("T110"))
        self.act_move_down.setToolTip(f"{t('T110')} (Alt+Down)")

        self.act_move_to.setText("Numaraya Taşı..." if i18n.current_language == "Türkçe" else "Move to Slot #...")
        self.act_move_to.setToolTip(f"{'Kanalı Numaraya Taşı' if i18n.current_language == 'Türkçe' else 'Move Channel to Slot #'} (Ctrl+M)")

        self.act_del_sel.setText(t("T111"))
        self.act_del_sel.setToolTip(f"{t('T111')} (Delete)")

        self.act_del_chk.setText(t("T112"))
        self.act_del_chk.setToolTip(t("T112"))

        self.act_compare.setText(t("T104"))
        self.act_compare.setToolTip(f"{t('T104')} (Ctrl+K)")

        self.act_import.setText(t("T105"))
        self.act_import.setToolTip(f"{t('T105')} (Ctrl+I)")

        self.act_move_radios_end.setText("Radyoları Listenin Sonuna Taşı" if is_tr else "Move Radios to End")
        self.act_remove_scrambled.setText("Şifreli Kanalları Sil..." if is_tr else "Remove Scrambled Channels...")
        self.act_normalize_names.setText("Kanal İsimlerini Standartlaştır" if is_tr else "Normalize Channel Names")
        self.act_remove_duplicates.setText("Çift / Mükerrer Kanalları Temizle..." if is_tr else "Remove Duplicate Channels...")
        self.act_ref_sort.setText("Referans Liste ile Sırala..." if is_tr else "Sort by Reference List...")

        self.act_toggle_sidebar.setText(t("T119"))
        self.act_toggle_sidebar.setToolTip(f"{t('T119')} (F4)")

        self.act_about.setText(t("T106"))
        self.act_about.setToolTip(f"{t('T106')} (F1)")

        self.act_shortcuts.setText("Klavye Kısayolları" if is_tr else "Keyboard Shortcuts")
        self.act_shortcuts.setToolTip(f"{'Klavye Kısayolları' if is_tr else 'Keyboard Shortcuts'} (Ctrl+/)")

        self.act_report_issue.setText("Hata Bildir / Geri Bildirim" if i18n.current_language == "Türkçe" else "Report Issue / Feedback")
        self.act_github_repo.setText("GitHub Deposu" if i18n.current_language == "Türkçe" else "GitHub Repository")
        self.act_check_updates.setText("Güncellemeleri Denetle..." if is_tr else "Check for Updates...")

        # Subcomponents
        self._rebuild_language_menu()
        self._update_status_lang_button()
        self.search_bar.retranslate_ui()
        self.channel_table.retranslate_ui()
        self.sidebar.retranslate_ui()
        self._update_channel_counts()

    def _on_language_changed(self, new_lang: str) -> None:
        """Updates all UI text dynamically when language is switched."""
        self.retranslate_ui()

