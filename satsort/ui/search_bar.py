"""
SatSort - Quick Search and Filter Bar Widget
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)

from ..i18n import t
from .theme import get_current_theme


class SearchBarWidget(QWidget):
    """
    Search and filter bar allowing instant channel filtering, match navigation, and Enter-key batch selection.
    """

    text_changed = Signal(str)
    search_confirmed = Signal(str)
    prev_match_requested = Signal()
    next_match_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Search icon label
        self._icon_label = QLabel("🔍")
        self._icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self._icon_label)

        # Search Input
        self._search_input = QLineEdit()
        self._search_input.setObjectName("search_input")
        self._search_input.setPlaceholderText(f"{t('T118')} Ara... (Enter: Sonraki / İşaretle)")
        self._search_input.setClearButtonEnabled(True)
        layout.addWidget(self._search_input, stretch=1)

        # Prev Match Button
        self._btn_prev = QPushButton("▲")
        self._btn_prev.setObjectName("search_nav_btn")
        self._btn_prev.setToolTip("Önceki Eşleşme (Shift+Enter)")
        self._btn_prev.setEnabled(False)
        self._btn_prev.setFixedSize(28, 28)
        layout.addWidget(self._btn_prev)

        # Next Match Button
        self._btn_next = QPushButton("▼")
        self._btn_next.setObjectName("search_nav_btn")
        self._btn_next.setToolTip("Sonraki Eşleşme (Enter)")
        self._btn_next.setEnabled(False)
        self._btn_next.setFixedSize(28, 28)
        layout.addWidget(self._btn_next)

        # Batch Mark Matches Button
        self._btn_mark_all = QPushButton("✔")
        self._btn_mark_all.setObjectName("search_mark_btn")
        self._btn_mark_all.setToolTip(f"{t('T143')} (Ctrl+Enter)")
        self._btn_mark_all.setEnabled(False)
        self._btn_mark_all.setFixedSize(28, 28)
        layout.addWidget(self._btn_mark_all)

        # Match Count Badge Label
        self._count_label = QLabel("")
        self._count_label.setObjectName("search_count_badge")
        self._count_label.setVisible(False)
        layout.addWidget(self._count_label)

        self._has_channels = False

        # Connect signals
        self._search_input.textChanged.connect(self._on_text_changed)
        self._search_input.returnPressed.connect(self._on_return_pressed)
        self._btn_prev.clicked.connect(lambda checked=False: self.prev_match_requested.emit())
        self._btn_next.clicked.connect(lambda checked=False: self.next_match_requested.emit())
        self._btn_mark_all.clicked.connect(lambda checked=False: self.search_confirmed.emit(self.get_text()))

    def set_has_channels(self, has_channels: bool) -> None:
        """Enables buttons for move operations when table has channels and no search is active."""
        self._has_channels = has_channels
        query = self.get_text()
        if not query:
            self._btn_prev.setEnabled(has_channels)
            self._btn_next.setEnabled(has_channels)
            self._btn_mark_all.setEnabled(has_channels)
            self._update_idle_tooltips()

    def _update_idle_tooltips(self) -> None:
        self._btn_prev.setToolTip(f"{t('T109')} (Alt+Up)")
        self._btn_next.setToolTip(f"{t('T110')} (Alt+Down)")
        self._btn_mark_all.setToolTip(f"{t('T108')} (Ctrl+A)")

    def _on_text_changed(self, text: str) -> None:
        clean = text.strip()
        if not clean:
            self._count_label.setVisible(False)
            self._btn_prev.setEnabled(self._has_channels)
            self._btn_next.setEnabled(self._has_channels)
            self._btn_mark_all.setEnabled(self._has_channels)
            self._update_idle_tooltips()
            self.clear_requested.emit()
        else:
            self.text_changed.emit(clean)

    def _on_return_pressed(self) -> None:
        clean = self._search_input.text().strip()
        if clean:
            self.next_match_requested.emit()

    def set_match_status(self, current_index: int, match_count: int, total: int) -> None:
        """Updates badge and navigation buttons based on current match index and total matches."""
        query = self.get_text()
        if not query:
            self._count_label.setVisible(False)
            self._btn_prev.setEnabled(self._has_channels)
            self._btn_next.setEnabled(self._has_channels)
            self._btn_mark_all.setEnabled(self._has_channels)
            self._update_idle_tooltips()
            return

        has_matches = match_count > 0
        self._btn_prev.setEnabled(has_matches)
        self._btn_next.setEnabled(has_matches)
        self._btn_mark_all.setEnabled(has_matches)
        self._btn_prev.setToolTip(f"{t('T109')} (Shift+Enter)")
        self._btn_next.setToolTip(f"{t('T110')} (Enter)")
        self._btn_mark_all.setToolTip(f"{t('T143')} (Ctrl+Enter)")

        is_light = get_current_theme() == "light"
        if has_matches:
            if current_index >= 0:
                self._count_label.setText(f"{current_index + 1} / {match_count} ({total} {t('T118')})")
            else:
                self._count_label.setText(f"{match_count} / {total} {t('T118')}")

            if is_light:
                self._count_label.setStyleSheet("""
                    QLabel {
                        background-color: #dbeafe;
                        color: #1e40af;
                        border: 1px solid #93c5fd;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
            else:
                self._count_label.setStyleSheet("""
                    QLabel {
                        background-color: #172554;
                        color: #60a5fa;
                        border: 1px solid #1e40af;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
        else:
            self._count_label.setText(f"0 / {total} {t('T118')}")
            if is_light:
                self._count_label.setStyleSheet("""
                    QLabel {
                        background-color: #fee2e2;
                        color: #991b1b;
                        border: 1px solid #fca5a5;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
            else:
                self._count_label.setStyleSheet("""
                    QLabel {
                        background-color: #450a0a;
                        color: #f87171;
                        border: 1px solid #991b1b;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                    }
                """)
        self._count_label.setVisible(True)

    def set_match_count(self, count: int, total: int) -> None:
        """Backward compatibility helper."""
        self.set_match_status(-1, count, total)

    def get_text(self) -> str:
        return self._search_input.text().strip()

    def clear(self) -> None:
        self._search_input.clear()
        self._count_label.setVisible(False)
        self._btn_prev.setEnabled(self._has_channels)
        self._btn_next.setEnabled(self._has_channels)
        self._btn_mark_all.setEnabled(self._has_channels)
        self._update_idle_tooltips()

    def retranslate_ui(self) -> None:
        """Dynamically retranslates placeholder, tooltips and labels."""
        self._search_input.setPlaceholderText(f"{t('T118')}... (Enter: Next / Mark)")
        if self.get_text():
            self._btn_prev.setToolTip(f"{t('T109')} (Shift+Enter)")
            self._btn_next.setToolTip(f"{t('T110')} (Enter)")
            self._btn_mark_all.setToolTip(f"{t('T143')} (Ctrl+Enter)")
        else:
            self._update_idle_tooltips()


