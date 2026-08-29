"""
SatSort - Channel Details & Transponder Package Sidebar Widget
"""

from __future__ import annotations
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QFrame,
)

from ..core.models import Channel, ChannelType, Polarization
from ..i18n import t
from .theme import get_current_theme
from .icons import get_icon


class ChannelParametersWidget(QGroupBox):
    """Displays comprehensive technical parameters of the selected satellite channel."""

    PARAM_KEYS = [
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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle(t("T119"))  # Kanal Parametreleri / Channel Parameters
        self._value_labels: Dict[str, QLabel] = {}
        self._title_labels: Dict[str, QLabel] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(6)

        bold_font = QFont()
        bold_font.setBold(True)

        for row, (i18n_key, attr_name) in enumerate(self.PARAM_KEYS):
            lbl_title = QLabel(t(i18n_key) + ":")
            lbl_title.setObjectName("param_title")
            layout.addWidget(lbl_title, row, 0)
            self._title_labels[attr_name] = lbl_title

            lbl_val = QLabel("-")
            lbl_val.setObjectName("param_value")
            lbl_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(lbl_val, row, 1)

            self._value_labels[attr_name] = lbl_val

    def retranslate_ui(self) -> None:
        self.setTitle(t("T119"))
        for i18n_key, attr_name in self.PARAM_KEYS:
            if attr_name in self._title_labels:
                self._title_labels[attr_name].setText(t(i18n_key) + ":")

    def set_channel(self, channel: Optional[Channel]) -> None:
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


class TransponderChannelsWidget(QGroupBox):
    """Lists other channels sharing the exact same frequency package/transponder."""

    channel_selected = Signal(object)  # Emits Channel

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle(t("T120"))  # Bu Paketteki Kanallar / Channels on this Package
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 8)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("transponder_list")
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

    def retranslate_ui(self) -> None:
        self.setTitle(t("T120"))

    def update_transponder_channels(
        self, selected_channel: Optional[Channel], all_channels: List[Channel]
    ) -> None:
        self.list_widget.clear()
        if not selected_channel:
            return

        target_key = selected_channel.transponder_key
        for ch in all_channels:
            if ch.transponder_key == target_key:
                icon_name = "tv" if ch.channel_type == ChannelType.TV else ("radio" if ch.channel_type == ChannelType.RADIO else "satellite_alt")
                item = QListWidgetItem(get_icon(icon_name, size=16), ch.channel_name)
                item.setData(Qt.UserRole, ch)
                if ch == selected_channel:
                    is_light = get_current_theme() == "light"
                    item.setForeground(QColor("#0284c7") if is_light else QColor("#60a5fa"))
                    item.setFont(QFont("", -1, QFont.Bold))
                self.list_widget.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        ch = item.data(Qt.UserRole)
        if ch:
            self.channel_selected.emit(ch)


class SidebarWidget(QWidget):
    """Unified right sidebar combining Channel Parameters card and Transponder Package list."""

    transponder_channel_clicked = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.params_widget = ChannelParametersWidget()
        content_layout.addWidget(self.params_widget)

        self.transponder_widget = TransponderChannelsWidget()
        self.transponder_widget.setMinimumHeight(200)
        self.transponder_widget.channel_selected.connect(self.transponder_channel_clicked)
        content_layout.addWidget(self.transponder_widget)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def set_channel(self, channel: Optional[Channel], all_channels: List[Channel]) -> None:
        self.params_widget.set_channel(channel)
        self.transponder_widget.update_transponder_channels(channel, all_channels)

    def retranslate_ui(self) -> None:
        self.params_widget.retranslate_ui()
        self.transponder_widget.retranslate_ui()

    def clear(self) -> None:
        self.params_widget.clear()

        self.transponder_widget.list_widget.clear()
