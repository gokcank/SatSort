"""
SatSort - Advanced Channel Table Widget with Drag-and-Drop & Context Menu
"""

from __future__ import annotations
from typing import List, Optional

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor, QFont, QAction, QIcon
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMenu,
    QMessageBox,
)

from ..core.models import Channel, ChannelType, Polarization
from ..i18n import t
from .theme import get_current_theme


class ChannelTableWidget(QTableWidget):
    """
    Table widget displaying satellite channels with drag-drop reordering,
    checkboxes, badges, and contextual management tools.
    """

    channel_selected = Signal(object)  # Emits selected Channel
    channels_updated = Signal()        # Emits when channels list or order changes
    request_rename = Signal(int, object)  # (row_index, Channel)
    request_move = Signal(bool)          # True if checked, False if single selected
    request_swap = Signal(int)           # source row

    COL_NO = 0
    COL_CHECK = 1
    COL_TYPE = 2
    COL_NAME = 3
    COL_SAT = 4
    COL_FREQ = 5
    COL_POL = 6
    COL_SR = 7
    COL_FEC = 8
    COL_CRYPTO = 9

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._channels: List[Channel] = []
        self._is_updating = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        headers = [
            t("T117"),  # Sıra / Order
            "✓",        # Check
            t("T124"),  # Tip / Type
            t("T123"),  # Kanal Adı / Name
            t("T122"),  # Uydu / Satellite
            t("T126"),  # Frekans / Frequency
            t("T127"),  # Polarizasyon / Pol
            t("T128"),  # Sembol Oranı / SR
            t("T129"),  # FEC
            t("T139"),  # Kripto / Crypto
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # Selection & Drag-and-drop settings
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.verticalHeader().setVisible(False)

        # Column sizing
        header = self.horizontalHeader()
        header.setSectionResizeMode(self.COL_NO, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_CHECK, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_TYPE, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_SAT, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_FREQ, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_POL, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_SR, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_FEC, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_CRYPTO, QHeaderView.ResizeToContents)

    def _connect_signals(self) -> None:
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemChanged.connect(self._on_item_changed)
        self.cellDoubleClicked.connect(self._on_double_click)

    def set_channels(self, channels: List[Channel]) -> None:
        """Loads and displays a new list of channels."""
        self._is_updating = True
        self._channels = list(channels)
        self.setRowCount(len(self._channels))

        bold_font = QFont()
        bold_font.setBold(True)

        for row, ch in enumerate(self._channels):
            # 0: Order No
            item_no = QTableWidgetItem(str(row + 1))
            item_no.setTextAlignment(Qt.AlignCenter)
            item_no.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_NO, item_no)

            # 1: Checkbox
            item_check = QTableWidgetItem()
            item_check.setCheckState(Qt.Checked if ch.is_checked else Qt.Unchecked)
            item_check.setTextAlignment(Qt.AlignCenter)
            item_check.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            self.setItem(row, self.COL_CHECK, item_check)

            # 2: Channel Type (Badge)
            type_label = "TV" if ch.channel_type == ChannelType.TV else (
                "Radio" if ch.channel_type == ChannelType.RADIO else (
                    "Data" if ch.channel_type == ChannelType.DATA else "Pkg"
                )
            )
            item_type = QTableWidgetItem(type_label)
            item_type.setTextAlignment(Qt.AlignCenter)
            item_type.setFont(bold_font)
            if ch.channel_type == ChannelType.TV:
                item_type.setForeground(QColor("#60a5fa"))  # Light Blue
            elif ch.channel_type == ChannelType.RADIO:
                item_type.setForeground(QColor("#a78bfa"))  # Light Purple
            elif ch.channel_type == ChannelType.DATA:
                item_type.setForeground(QColor("#34d399"))  # Green
            else:
                item_type.setForeground(QColor("#94a3b8"))  # Gray
            item_type.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_TYPE, item_type)

            # 3: Channel Name
            item_name = QTableWidgetItem(ch.channel_name)
            item_name.setFont(bold_font)
            item_name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_NAME, item_name)

            # 4: Satellite
            item_sat = QTableWidgetItem(ch.satellite_name)
            item_sat.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_SAT, item_sat)

            # 5: Frequency
            item_freq = QTableWidgetItem(ch.frequency)
            item_freq.setTextAlignment(Qt.AlignCenter)
            item_freq.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_FREQ, item_freq)

            # 6: Polarization
            pol_text = "V" if ch.polarization == Polarization.VERTICAL else "H"
            item_pol = QTableWidgetItem(pol_text)
            item_pol.setTextAlignment(Qt.AlignCenter)
            item_pol.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_POL, item_pol)

            # 7: Symbol Rate
            item_sr = QTableWidgetItem(ch.symbol_rate)
            item_sr.setTextAlignment(Qt.AlignCenter)
            item_sr.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_SR, item_sr)

            # 8: FEC
            item_fec = QTableWidgetItem(ch.fec)
            item_fec.setTextAlignment(Qt.AlignCenter)
            item_fec.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_FEC, item_fec)

            # 9: Crypto
            crypto_text = ch.crypto.strip()
            item_crypto = QTableWidgetItem(crypto_text if crypto_text else "-")
            item_crypto.setTextAlignment(Qt.AlignCenter)
            item_crypto.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.setItem(row, self.COL_CRYPTO, item_crypto)

            # Row background highlight for checked items
            self._update_row_visual(row, ch.is_checked)

        self._is_updating = False
        self.channels_updated.emit()

    def _update_row_visual(self, row: int, is_checked: bool) -> None:
        """Applies visual highlighting to checked rows based on theme."""
        if get_current_theme() == "light":
            bg_color = QColor("#fef3c7") if is_checked else QColor("#ffffff")
        else:
            bg_color = QColor("#2e2608") if is_checked else QColor("#14171d")

        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(bg_color)

    def _on_selection_changed(self) -> None:
        selected_rows = self.get_selected_row_indices()
        if selected_rows and 0 <= selected_rows[0] < len(self._channels):
            self.channel_selected.emit(self._channels[selected_rows[0]])

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        if self._is_updating or item.column() != self.COL_CHECK:
            return

        row = item.row()
        if 0 <= row < len(self._channels):
            is_checked = (item.checkState() == Qt.Checked)
            self._channels[row].is_checked = is_checked
            self._update_row_visual(row, is_checked)
            self.channels_updated.emit()

    def _on_double_click(self, row: int, column: int) -> None:
        if 0 <= row < len(self._channels):
            self.request_rename.emit(row, self._channels[row])

    def get_channels(self) -> List[Channel]:
        return self._channels

    def get_selected_row_indices(self) -> List[int]:
        rows = sorted(list(set(index.row() for index in self.selectedIndexes())))
        return rows

    def get_selected_channel(self) -> Optional[Channel]:
        rows = self.get_selected_row_indices()
        if rows and 0 <= rows[0] < len(self._channels):
            return self._channels[rows[0]]
        return None

    def get_checked_row_indices(self) -> List[int]:
        return [i for i, ch in enumerate(self._channels) if ch.is_checked]

    def get_checked_channels(self) -> List[Channel]:
        return [ch for ch in self._channels if ch.is_checked]

    def update_channel_order_numbers(self) -> None:
        """Refreshes the sequential row numbers."""
        self._is_updating = True
        for row in range(len(self._channels)):
            item = self.item(row, self.COL_NO)
            if item:
                item.setText(str(row + 1))
        self._is_updating = False
        self.channels_updated.emit()

    def move_channel(self, source_row: int, target_row: int) -> bool:
        """Moves a single channel from source index to target index."""
        if not (0 <= source_row < len(self._channels)) or not (0 <= target_row < len(self._channels)):
            return False
        if source_row == target_row:
            return True

        channel = self._channels.pop(source_row)
        self._channels.insert(target_row, channel)
        self.set_channels(self._channels)
        self.selectRow(target_row)
        return True

    def move_selected_up(self) -> None:
        rows = self.get_selected_row_indices()
        if not rows or rows[0] == 0:
            return
        self.move_channel(rows[0], rows[0] - 1)

    def move_selected_down(self) -> None:
        rows = self.get_selected_row_indices()
        if not rows or rows[0] >= len(self._channels) - 1:
            return
        self.move_channel(rows[0], rows[0] + 1)

    def swap_channels(self, idx1: int, idx2: int) -> bool:
        if not (0 <= idx1 < len(self._channels)) or not (0 <= idx2 < len(self._channels)):
            return False
        self._channels[idx1], self._channels[idx2] = self._channels[idx2], self._channels[idx1]
        self.set_channels(self._channels)
        self.selectRow(idx2)
        return True

    def move_checked_channels(self, target_idx: int) -> bool:
        """Moves all checked channels to a target index position."""
        checked_indices = self.get_checked_row_indices()
        if not checked_indices or not (0 <= target_idx < len(self._channels)):
            return False

        checked_items = [self._channels[i] for i in checked_indices]
        # Remove from high to low to maintain index validity
        for i in reversed(checked_indices):
            self._channels.pop(i)

        # Adjust insertion point if moving downwards
        adjusted_target = min(target_idx, len(self._channels))
        for item in reversed(checked_items):
            self._channels.insert(adjusted_target, item)

        self.set_channels(self._channels)
        return True

    def delete_selected(self) -> None:
        rows = self.get_selected_row_indices()
        if not rows:
            return
        for r in reversed(rows):
            if 0 <= r < len(self._channels):
                self._channels.pop(r)
        self.set_channels(self._channels)

    def delete_checked(self) -> None:
        checked_indices = self.get_checked_row_indices()
        if not checked_indices:
            return
        for r in reversed(checked_indices):
            self._channels.pop(r)
        self.set_channels(self._channels)

    def uncheck_all(self) -> None:
        for ch in self._channels:
            ch.is_checked = False
        self.set_channels(self._channels)

    def check_all(self) -> None:
        for ch in self._channels:
            ch.is_checked = True
        self.set_channels(self._channels)

    def update_channel_name_at(self, row: int, new_name: str) -> None:
        if 0 <= row < len(self._channels):
            self._channels[row].channel_name = new_name
            item = self.item(row, self.COL_NAME)
            if item:
                item.setText(new_name)
            self.channel_selected.emit(self._channels[row])
            self.channels_updated.emit()

    def dropEvent(self, event) -> None:
        """Handles internal drag-drop row reordering."""
        selected_rows = self.get_selected_row_indices()
        if not selected_rows:
            event.ignore()
            return

        drop_pos = event.position().toPoint()
        drop_row = self.rowAt(drop_pos.y())
        if drop_row == -1:
            drop_row = self.rowCount() - 1

        source_row = selected_rows[0]
        if source_row != drop_row:
            self.move_channel(source_row, drop_row)
            event.accept()
        else:
            event.ignore()

    def contextMenuEvent(self, event) -> None:
        """Renders the contextual right-click menu."""
        menu = QMenu(self)
        selected_ch = self.get_selected_channel()
        has_selection = selected_ch is not None
        has_checked = len(self.get_checked_row_indices()) > 0

        # Actions
        act_up = QAction(t("T109"), self)  # Yukarı Taşı
        act_up.setEnabled(has_selection)
        act_up.triggered.connect(self.move_selected_up)
        menu.addAction(act_up)

        act_down = QAction(t("T110"), self)  # Aşağı Taşı
        act_down.setEnabled(has_selection)
        act_down.triggered.connect(self.move_selected_down)
        menu.addAction(act_down)

        menu.addSeparator()

        act_move_sel = QAction(t("T113"), self)  # Seçili Kanalı Taşı
        act_move_sel.setEnabled(has_selection)
        act_move_sel.triggered.connect(lambda: self.request_move.emit(False))
        menu.addAction(act_move_sel)

        act_move_chk = QAction(t("T114"), self)  # İşaretli Kanalları Taşı
        act_move_chk.setEnabled(has_checked)
        act_move_chk.triggered.connect(lambda: self.request_move.emit(True))
        menu.addAction(act_move_chk)

        act_swap = QAction(t("T115"), self)  # Takas Et
        act_swap.setEnabled(has_selection)
        act_swap.triggered.connect(lambda: self.request_swap.emit(self.get_selected_row_indices()[0]))
        menu.addAction(act_swap)

        menu.addSeparator()

        act_rename = QAction(t("T116"), self)  # Kanal Adını Değiştir
        act_rename.setEnabled(has_selection)
        act_rename.triggered.connect(
            lambda: self.request_rename.emit(self.get_selected_row_indices()[0], selected_ch)
        )
        menu.addAction(act_rename)

        menu.addSeparator()

        act_del_sel = QAction(t("T111"), self)  # Seçiliyi Sil
        act_del_sel.setEnabled(has_selection)
        act_del_sel.triggered.connect(self.delete_selected)
        menu.addAction(act_del_sel)

        act_del_chk = QAction(t("T112"), self)  # İşaretlileri Sil
        act_del_chk.setEnabled(has_checked)
        act_del_chk.triggered.connect(self.delete_checked)
        menu.addAction(act_del_chk)

        menu.addSeparator()

        act_uncheck = QAction(t("T108"), self)  # Tüm İşaretleri Kaldır
        act_uncheck.triggered.connect(self.uncheck_all)
        menu.addAction(act_uncheck)

        menu.exec(event.globalPos())
