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


class SearchBarWidget(QWidget):
    """
    Search and filter bar allowing instant channel filtering and Enter-key batch selection.
    """

    text_changed = Signal(str)
    search_confirmed = Signal(str)
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search icon label
        self._icon_label = QLabel("🔍")
        self._icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self._icon_label)

        # Search Input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(f"{t('T118')} Ara... (Enter: {t('T143').split()[-1]})")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 12px;
                color: #f8fafc;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(self._search_input, stretch=1)

        # Match Count Badge Label
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        self._count_label.setVisible(False)
        layout.addWidget(self._count_label)

        # Connect signals
        self._search_input.textChanged.connect(self._on_text_changed)
        self._search_input.returnPressed.connect(self._on_return_pressed)

    def _on_text_changed(self, text: str) -> None:
        clean = text.strip()
        if not clean:
            self._count_label.setVisible(False)
            self.clear_requested.emit()
        else:
            self.text_changed.emit(clean)

    def _on_return_pressed(self) -> None:
        clean = self._search_input.text().strip()
        if clean:
            self.search_confirmed.emit(clean)

    def set_match_count(self, count: int, total: int) -> None:
        """Updates the badge showing how many channels matched the query."""
        if self._search_input.text().strip():
            self._count_label.setText(f"{count} / {total} {t('T118')}")
            if count > 0:
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
        else:
            self._count_label.setVisible(False)

    def get_text(self) -> str:
        return self._search_input.text().strip()

    def clear(self) -> None:
        self._search_input.clear()
        self._count_label.setVisible(False)
