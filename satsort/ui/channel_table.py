"""
SatSort - Advanced Channel Table Widget with Drag-and-Drop & Context Menu
"""

from __future__ import annotations
from typing import List, Optional

from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtGui import QColor, QFont, QAction, QIcon, QPainter, QPen
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
        self._drag_active = False
        self._drop_target_row: Optional[int] = None
        self._search_match_rows: List[int] = []
        self._current_match_index: int = -1

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
        self.viewport().setAcceptDrops(True)
        self.setAutoScroll(True)
        self.setAutoScrollMargin(40)
        self.setDropIndicatorShown(False)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragDropOverwriteMode(False)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.verticalHeader().setVisible(False)

        # Column sizing (Interactive resizing)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        self.setColumnWidth(self.COL_NO, 55)
        self.setColumnWidth(self.COL_CHECK, 35)
        self.setColumnWidth(self.COL_TYPE, 65)
        self.setColumnWidth(self.COL_NAME, 220)
        self.setColumnWidth(self.COL_SAT, 140)
        self.setColumnWidth(self.COL_FREQ, 80)
        self.setColumnWidth(self.COL_POL, 55)
        self.setColumnWidth(self.COL_SR, 75)
        self.setColumnWidth(self.COL_FEC, 65)
        self.setColumnWidth(self.COL_CRYPTO, 80)

    def _connect_signals(self) -> None:
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemChanged.connect(self._on_item_changed)
        self.cellDoubleClicked.connect(self._on_double_click)

    def set_channels(self, channels: List[Channel]) -> None:
        """Loads and displays a new list of channels."""
        self._is_updating = True
        self.setUpdatesEnabled(False)
        self.blockSignals(True)
        self._channels = list(channels)
        
        # Clear the table cleanly before repopulating to prevent stale items
        self.setRowCount(0)
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
            is_light = get_current_theme() == "light"
            if ch.channel_type == ChannelType.TV:
                item_type.setForeground(QColor("#0284c7") if is_light else QColor("#60a5fa"))  # Deep vs Light Blue
            elif ch.channel_type == ChannelType.RADIO:
                item_type.setForeground(QColor("#7c3aed") if is_light else QColor("#a78bfa"))  # Deep vs Light Purple
            elif ch.channel_type == ChannelType.DATA:
                item_type.setForeground(QColor("#047857") if is_light else QColor("#34d399"))  # Deep Green vs Mint
            else:
                item_type.setForeground(QColor("#475569") if is_light else QColor("#94a3b8"))  # Slate vs Light Gray
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

        self.blockSignals(False)
        self.setUpdatesEnabled(True)
        self._is_updating = False
        self.channels_updated.emit()

    def _update_row_visual(self, row: int, is_checked: bool) -> None:
        """Applies visual highlighting to checked rows based on theme."""
        prev_updating = self._is_updating
        self._is_updating = True
        if get_current_theme() == "light":
            bg_color = QColor("#fef3c7") if is_checked else QColor("#ffffff")
        else:
            bg_color = QColor("#2e2608") if is_checked else QColor("#14171d")

        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(bg_color)
        self._is_updating = prev_updating

    def _on_selection_changed(self) -> None:
        if self._is_updating:
            return
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
        """Moves a single channel from source index to target index efficiently in O(1) row ops."""
        if not (0 <= source_row < len(self._channels)) or not (0 <= target_row < len(self._channels)):
            return False
        if source_row == target_row:
            return True

        self._is_updating = True
        self.setUpdatesEnabled(False)
        self.blockSignals(True)

        # 1. Update data model
        ch = self._channels.pop(source_row)
        self._channels.insert(target_row, ch)

        # 2. Extract items to prevent deletion
        items = []
        for col in range(self.columnCount()):
            items.append(self.takeItem(source_row, col))

        # 3. Update table structure cleanly
        self.removeRow(source_row)
        self.insertRow(target_row)

        # 4. Insert items at new position
        for col in range(self.columnCount()):
            self.setItem(target_row, col, items[col])

        # 5. Update row numbers for affected rows
        start = min(source_row, target_row)
        end = max(source_row, target_row)
        for r in range(start, end + 1):
            item_no = self.item(r, self.COL_NO)
            if item_no:
                item_no.setText(str(r + 1))

        self.blockSignals(False)
        self.setUpdatesEnabled(True)
        self._is_updating = False

        self.selectRow(target_row)
        self.channels_updated.emit()
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

    def move_multiple_channels(self, source_rows: List[int], target_row: int) -> bool:
        """Moves a block of multiple channels to a target row position."""
        if not source_rows or not (0 <= target_row <= len(self._channels)):
            return False

        unique_sources = sorted(list(set(source_rows)))
        if not unique_sources:
            return False

        channels_to_move = [self._channels[r] for r in unique_sources]

        # Calculate insertion index in remaining channels list
        offset = sum(1 for r in unique_sources if r < target_row)
        insert_pos = max(0, min(target_row - offset, len(self._channels) - len(channels_to_move)))

        # Remove source channels from highest index to lowest
        for r in reversed(unique_sources):
            del self._channels[r]

        # Insert at new position
        for i, ch in enumerate(channels_to_move):
            self._channels.insert(insert_pos + i, ch)

        # Repopulate table
        self.set_channels(self._channels)

        # Re-select the moved block of rows
        self.clearSelection()
        for r in range(insert_pos, insert_pos + len(channels_to_move)):
            self.selectRow(r)

        first_item = self.item(insert_pos, 0)
        if first_item:
            self.scrollToItem(first_item)

        self.channels_updated.emit()
        return True

    def smart_delete(self) -> int:
        """
        Deletes checked channels if any are checked; otherwise deletes selected rows.
        Returns the number of deleted channels.
        """
        checked_indices = self.get_checked_row_indices()
        if checked_indices:
            deleted_count = len(checked_indices)
            self.delete_checked()
            return deleted_count

        selected_indices = self.get_selected_row_indices()
        if selected_indices:
            deleted_count = len(selected_indices)
            self.delete_selected()
            return deleted_count

        return 0

    def delete_selected(self) -> None:
        rows = self.get_selected_row_indices()
        if not rows:
            return
        for r in reversed(rows):
            if 0 <= r < len(self._channels):
                self._channels.pop(r)
        self.set_channels(self._channels)
        if self._channels:
            next_row = min(rows[0], len(self._channels) - 1)
            self.selectRow(next_row)
        self.channels_updated.emit()

    def delete_checked(self) -> None:
        checked_indices = self.get_checked_row_indices()
        if not checked_indices:
            return
        for r in reversed(checked_indices):
            self._channels.pop(r)
        self.set_channels(self._channels)
        if self._channels:
            next_row = min(checked_indices[0], len(self._channels) - 1)
            self.selectRow(next_row)
        self.channels_updated.emit()

    def uncheck_all(self) -> None:
        self._is_updating = True
        for row, ch in enumerate(self._channels):
            ch.is_checked = False
            item = self.item(row, self.COL_CHECK)
            if item:
                item.setCheckState(Qt.Unchecked)
            self._update_row_visual(row, False)
        self._is_updating = False
        self.channels_updated.emit()

    def check_all(self) -> None:
        self._is_updating = True
        for row, ch in enumerate(self._channels):
            ch.is_checked = True
            item = self.item(row, self.COL_CHECK)
            if item:
                item.setCheckState(Qt.Checked)
            self._update_row_visual(row, True)
        self._is_updating = False
        self.channels_updated.emit()

    def is_all_checked(self) -> bool:
        """Returns True if all channels are checked (and at least one channel exists)."""
        if not self._channels:
            return False
        return all(ch.is_checked for ch in self._channels)

    def toggle_all_checked(self) -> bool:
        """
        Toggles check state for all channels:
        If all channels are checked, unchecks all.
        Otherwise, checks all channels.
        Returns True if channels are now all checked, False otherwise.
        """
        if not self._channels:
            return False

        if self.is_all_checked():
            self.uncheck_all()
            return False
        else:
            self.check_all()
            return True

    def search_channels(self, query: str) -> List[int]:
        """
        Finds all channels matching the query (substring in channel_name),
        updates match state, highlights first match and repaints scrollbar ticks.
        """
        lower_q = query.strip().lower()
        if not lower_q:
            self.clear_search_matches()
            return []

        self._search_match_rows = [
            i for i, ch in enumerate(self._channels)
            if lower_q in ch.channel_name.lower()
        ]

        if self._search_match_rows:
            self._current_match_index = 0
            first_row = self._search_match_rows[0]
            self.selectRow(first_row)
            first_item = self.item(first_row, 0)
            if first_item:
                self.scrollToItem(first_item, QAbstractItemView.PositionAtCenter)
            if 0 <= first_row < len(self._channels):
                self.channel_selected.emit(self._channels[first_row])
        else:
            self._current_match_index = -1

        self.viewport().update()
        return self._search_match_rows

    def goto_next_match(self) -> int:
        """Navigates to the next matching channel row in search results."""
        if not self._search_match_rows:
            return -1

        self._current_match_index = (self._current_match_index + 1) % len(self._search_match_rows)
        target_row = self._search_match_rows[self._current_match_index]
        self.selectRow(target_row)
        item = self.item(target_row, 0)
        if item:
            self.scrollToItem(item, QAbstractItemView.PositionAtCenter)
        if 0 <= target_row < len(self._channels):
            self.channel_selected.emit(self._channels[target_row])

        self.viewport().update()
        return self._current_match_index

    def goto_prev_match(self) -> int:
        """Navigates to the previous matching channel row in search results."""
        if not self._search_match_rows:
            return -1

        self._current_match_index = (self._current_match_index - 1 + len(self._search_match_rows)) % len(self._search_match_rows)
        target_row = self._search_match_rows[self._current_match_index]
        self.selectRow(target_row)
        item = self.item(target_row, 0)
        if item:
            self.scrollToItem(item, QAbstractItemView.PositionAtCenter)
        if 0 <= target_row < len(self._channels):
            self.channel_selected.emit(self._channels[target_row])

        self.viewport().update()
        return self._current_match_index

    def get_search_matches(self) -> List[int]:
        return list(self._search_match_rows)

    def get_current_match_index(self) -> int:
        return self._current_match_index

    def clear_search_matches(self) -> None:
        self._search_match_rows = []
        self._current_match_index = -1
        self.viewport().update()

    def mark_matching_channels(self, query: str) -> int:
        """Marks matching channels as checked in-place without rebuilding the table."""
        lower_q = query.strip().lower()
        if not lower_q:
            return 0

        self._is_updating = True
        match_count = 0
        first_match_row = -1

        for row, ch in enumerate(self._channels):
            if lower_q in ch.channel_name.lower():
                ch.is_checked = True
                match_count += 1
                if first_match_row == -1:
                    first_match_row = row
                item = self.item(row, self.COL_CHECK)
                if item:
                    item.setCheckState(Qt.Checked)
                self._update_row_visual(row, True)

        self._is_updating = False
        self.channels_updated.emit()

        if first_match_row != -1:
            self.selectRow(first_match_row)
            first_item = self.item(first_match_row, 0)
            if first_item:
                self.scrollToItem(first_item)

        return match_count

    def update_channel_name_at(self, row: int, new_name: str) -> None:
        if 0 <= row < len(self._channels):
            self._channels[row].channel_name = new_name
            item = self.item(row, self.COL_NAME)
            if item:
                item.setText(new_name)
            self.channel_selected.emit(self._channels[row])
            self.channels_updated.emit()

    def dragEnterEvent(self, event) -> None:
        if event.source() == self:
            self._drag_active = True
            self._drop_target_row = None
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.source() == self:
            pos = event.position().toPoint()
            y = pos.y()
            vh = self.viewport().height()
            margin = 40

            # Smooth edge auto-scrolling
            if y < margin:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 4)
            elif y > vh - margin:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 4)

            drop_row = self.rowAt(y)
            if drop_row == -1:
                drop_row = max(0, len(self._channels))
            else:
                row_rect = self.visualRect(self.model().index(drop_row, 0))
                if y > row_rect.center().y():
                    drop_row = min(len(self._channels), drop_row + 1)

            self._drop_target_row = drop_row
            self.viewport().update()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._drag_active = False
        self._drop_target_row = None
        self.viewport().update()
        event.accept()

    def dropEvent(self, event) -> None:
        """Handles multi-channel drag-drop row reordering cleanly without leaving empty rows."""
        if event.source() != self:
            event.ignore()
            return

        self._drag_active = False
        target_row = self._drop_target_row
        self._drop_target_row = None
        self.viewport().update()

        selected_rows = self.get_selected_row_indices()
        if not selected_rows:
            event.ignore()
            return

        if target_row is None:
            drop_pos = event.position().toPoint()
            drop_row = self.rowAt(drop_pos.y())
            if drop_row == -1:
                target_row = len(self._channels)
            else:
                row_rect = self.visualRect(self.model().index(drop_row, 0))
                target_row = drop_row + 1 if drop_pos.y() > row_rect.center().y() else drop_row

        QTimer.singleShot(0, lambda s=selected_rows, t=target_row: self.move_multiple_channels(s, t))
        event.setDropAction(Qt.IgnoreAction)
        event.accept()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        # 1. Draw Drag-and-drop indicator line
        if self._drag_active and self._drop_target_row is not None and self.rowCount() > 0:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)

            if self._drop_target_row >= self.rowCount():
                rect = self.visualRect(self.model().index(self.rowCount() - 1, 0))
                line_y = rect.bottom()
            else:
                rect = self.visualRect(self.model().index(self._drop_target_row, 0))
                line_y = rect.top()

            width = self.viewport().width()
            # Outer glow line
            pen_glow = QPen(QColor(56, 189, 248, 120), 5)
            painter.setPen(pen_glow)
            painter.drawLine(0, line_y, width, line_y)

            # Core crisp line
            pen_line = QPen(QColor(56, 189, 248, 255), 2)
            painter.setPen(pen_line)
            painter.drawLine(0, line_y, width, line_y)

            # Indicator circular markers on edges
            painter.setBrush(QColor(56, 189, 248))
            painter.drawEllipse(QPoint(6, line_y), 4, 4)
            painter.drawEllipse(QPoint(width - 6, line_y), 4, 4)
            painter.end()

        # 2. Draw search result scrollbar tick marks along right edge
        if self._search_match_rows and self.rowCount() > 0:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            vw = self.viewport().width()
            vh = self.viewport().height()
            total_rows = self.rowCount()
            for r in self._search_match_rows:
                y_ratio = r / max(1, total_rows)
                tick_y = int(y_ratio * vh)
                is_current = (self._current_match_index >= 0 and r == self._search_match_rows[self._current_match_index])
                color = QColor(251, 146, 60, 255) if is_current else QColor(56, 189, 248, 200)
                pen = QPen(color, 3 if is_current else 2)
                painter.setPen(pen)
                painter.drawLine(vw - 8, tick_y, vw - 1, tick_y)
            painter.end()

    def contextMenuEvent(self, event) -> None:
        """Renders the dynamic contextual right-click menu."""
        clicked_row = self.rowAt(event.pos().y())
        if clicked_row != -1:
            self.selectRow(clicked_row)

        sel_indices = self.get_selected_row_indices()
        target_row = clicked_row if clicked_row != -1 else (sel_indices[0] if sel_indices else -1)

        menu = QMenu(self)
        selected_ch = self._channels[target_row] if (0 <= target_row < len(self._channels)) else self.get_selected_channel()
        has_selection = selected_ch is not None and target_row != -1
        checked_indices = self.get_checked_row_indices()
        checked_count = len(checked_indices)

        # Actions
        act_up = QAction(t("T109"), self)  # Yukarı Taşı
        act_up.setEnabled(has_selection)
        act_up.triggered.connect(lambda: QTimer.singleShot(0, self.move_selected_up))
        menu.addAction(act_up)

        act_down = QAction(t("T110"), self)  # Aşağı Taşı
        act_down.setEnabled(has_selection)
        act_down.triggered.connect(lambda: QTimer.singleShot(0, self.move_selected_down))
        menu.addAction(act_down)

        menu.addSeparator()

        act_move_sel = QAction(t("T113"), self)  # Seçili Kanalı Taşı
        act_move_sel.setEnabled(has_selection)
        act_move_sel.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.request_move.emit(False)))
        menu.addAction(act_move_sel)

        if checked_count > 0:
            act_move_chk = QAction(f"{t('T114')} ({checked_count})", self)  # İşaretli Kanalları Taşı (X)
            act_move_chk.triggered.connect(lambda: QTimer.singleShot(0, lambda: self.request_move.emit(True)))
            menu.addAction(act_move_chk)

        menu.addSeparator()

        act_rename = QAction(t("T116"), self)  # Kanal Adını Değiştir
        act_rename.setEnabled(has_selection)
        act_rename.triggered.connect(
            lambda checked=False, r=target_row, c=selected_ch: self.request_rename.emit(r, c) if c else None
        )
        menu.addAction(act_rename)

        menu.addSeparator()

        # Dynamic Delete options
        act_del_single = QAction("🗑️ " + t("T111"), self)  # Bu Kanalı Sil / Seçiliyi Sil
        act_del_single.setEnabled(has_selection)
        act_del_single.triggered.connect(lambda: QTimer.singleShot(0, self.delete_selected))
        menu.addAction(act_del_single)

        if checked_count > 0:
            act_del_chk = QAction(f"❌ {t('T112')} ({checked_count} {t('T118')})", self)  # İşaretli Kanalları Sil (X Kanal)
            act_del_chk.triggered.connect(lambda: QTimer.singleShot(0, self.delete_checked))
            menu.addAction(act_del_chk)

        menu.addSeparator()

        act_uncheck = QAction(t("T108"), self)  # Tüm İşaretleri Kaldır
        act_uncheck.setEnabled(checked_count > 0)
        act_uncheck.triggered.connect(lambda: QTimer.singleShot(0, self.uncheck_all))
        menu.addAction(act_uncheck)

        menu.exec(event.globalPos())

    def retranslate_ui(self) -> None:
        """Updates table headers on language switch."""
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
        self.setHorizontalHeaderLabels(headers)

