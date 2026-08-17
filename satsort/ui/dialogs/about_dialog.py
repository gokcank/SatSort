"""
SatSort - About Application Dialog
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from ...i18n import t


class AboutDialog(QDialog):
    """Dialog displaying application information, credits, and open source license details."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T106"))  # Hakkında / About
        self.setFixedSize(450, 320)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)

        # Header Badge
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("🛰️")
        icon_lbl.setStyleSheet("font-size: 38px;")
        header_layout.addWidget(icon_lbl)

        title_layout = QVBoxLayout()
        title_lbl = QLabel("SatSort")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #60a5fa;")
        title_layout.addWidget(title_lbl)

        ver_lbl = QLabel("v1.0.0 — Linux Native SatcoDX Editor")
        ver_lbl.setStyleSheet("color: #94a3b8; font-size: 13px;")
        title_layout.addWidget(ver_lbl)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #334155;")
        layout.addWidget(line)

        # Description text
        desc_lbl = QLabel(
            "SatSort, uydu alıcıları için <b>SatcoDX (.sdx)</b> formatındaki kanal "
            "listelerini Linux üzerinde yerel, hızlı ve modern bir arayüzle düzenleme, "
            "sıralama, filtreleme ve karşılaştırma aracıdır.<br><br>"
            "<b>Esinlenme & Teşekkür:</b><br>"
            "Bu proje, <b>Mehmet Taşköprü</b> tarafından geliştirilen açık kaynaklı "
            "<i>NovaSatcoDX</i> projesinden esinlenilerek Linux için sıfırdan "
            "Python & Qt6 (PySide6) ile geliştirilmiştir."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        layout.addStretch()

        # Close Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton(t("T107"))  # Kapat
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
