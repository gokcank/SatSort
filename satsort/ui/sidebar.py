"""
SatSort - Channel Details & Parameters Sidebar Widget
"""

from __future__ import annotations
from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFrame,
)

from ..core.models import Channel
from ..i18n import t


class ChannelParametersWidget(QGroupBox):
    """Displays comprehensive technical parameters of the selected satellite channel."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle(t("T119"))  # Kanal Parametreleri / Channel Parameters
        self._value_labels: Dict[str, QLabel] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(6)

        param_keys = [
            ("T122", "satellite_name"),   # Uydu Adı
            ("T123", "channel_name"),     # Kanal Adı
            ("T124", "channel_type"),     # Kanal Tipi
            ("T125", "broadcast_system"), # Broadcast Sistem
            ("T126", "frequency"),        # Frekans
            ("T127", "polarization"),     # Polarizasyon
            ("T128", "symbol_rate"),      # Sembol Oranı
            ("T129", "fec"),              # FEC
            ("T130", "vpid"),             # VPID
            ("T131", "apid"),             # APID
            ("T132", "pcrp"),             # PCRP
            ("T133", "sid"),              # SID
            ("T134", "nid"),              # NID
            ("T135", "tsid"),             # TSID
            ("T136", "language"),         # Dil
            ("T137", "country_code"),     # Ülke Kodu
            ("T138", "language_code"),    # Dil Kodu
            ("T139", "crypto"),           # Kripto
        ]

        bold_font = QFont()
        bold_font.setBold(True)

        for row, (i18n_key, attr_name) in enumerate(param_keys):
            lbl_title = QLabel(t(i18n_key) + ":")
            lbl_title.setStyleSheet("color: #94a3b8; font-size: 12px;")
            layout.addWidget(lbl_title, row, 0)

            lbl_val = QLabel("-")
            lbl_val.setStyleSheet("color: #f1f5f9; font-size: 12px; font-weight: bold;")
            lbl_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(lbl_val, row, 1)

            self._value_labels[attr_name] = lbl_val

    def set_channel(self, channel: Optional[Channel]) -> None:
        """Updates the parameter display with details of the selected channel."""
        if not channel:
            self.clear()
            return

        pol_display = channel.polarization.value if hasattr(channel.polarization, "value") else str(channel.polarization)
        ctype_display = channel.channel_type.value if hasattr(channel.channel_type, "value") else str(channel.channel_type)

        values = {
            "satellite_name": channel.satellite_name or "-",
            "channel_name": channel.channel_name or "-",
            "channel_type": ctype_display,
            "broadcast_system": channel.broadcast_system or "-",
            "frequency": channel.frequency or "-",
            "polarization": pol_display,
            "symbol_rate": channel.symbol_rate or "-",
            "fec": channel.fec or "-",
            "vpid": channel.vpid or "-",
            "apid": channel.apid or "-",
            "pcrp": channel.pcrp or "-",
            "sid": channel.sid or "-",
            "nid": channel.nid or "-",
            "tsid": channel.tsid or "-",
            "language": channel.language or "-",
            "country_code": channel.country_code or "-",
            "language_code": channel.language_code or "-",
            "crypto": channel.crypto or "-",
        }

        for attr, val in values.items():
            if attr in self._value_labels:
                self._value_labels[attr].setText(val)

    def clear(self) -> None:
        for lbl in self._value_labels.values():
            lbl.setText("-")
