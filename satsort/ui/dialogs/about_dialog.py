"""
SatSort - About Application Dialog
"""

from __future__ import annotations
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from ...i18n import t, i18n
from ... import __version__


class AboutDialog(QDialog):
    """Dialog displaying application information, credits, developer links, and report buttons."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T106"))  # Hakkında / About
        self.setFixedSize(480, 360)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        # Header Badge
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("🛰️")
        icon_lbl.setStyleSheet("font-size: 38px;")
        header_layout.addWidget(icon_lbl)

        title_layout = QVBoxLayout()
        title_lbl = QLabel("SatSort")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #60a5fa;")
        title_layout.addWidget(title_lbl)

        ver_lbl = QLabel(f"v{__version__} — Linux Native SatcoDX Editor")
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

        # Description text with clickable developer and repo links
        is_tr = i18n.current_language == "Türkçe"
        desc_lbl = QLabel(
            f"SatSort, uydu alıcıları için <b>SatcoDX (.sdx)</b> formatındaki kanal "
            f"listelerini Linux üzerinde yerel, hızlı ve modern bir arayüzle düzenleme, "
            f"sıralama ve karşılaştırma aracıdır.<br><br>"
            f"<b>{'Geliştirici' if is_tr else 'Developer'}:</b> "
            f"<a href='https://github.com/gokcank' style='color: #38bdf8; text-decoration: none;'><b>Gökcan</b> (github.com/gokcank)</a><br>"
            f"<b>{'Kaynak Kodu' if is_tr else 'Source Code'}:</b> "
            f"<a href='https://github.com/gokcank/SatSort' style='color: #38bdf8; text-decoration: none;'>github.com/gokcank/SatSort</a><br><br>"
            f"<b>{'Esinlenme & Teşekkür' if is_tr else 'Credits & Thanks'}:</b><br>"
            f"Mehmet Taşköprü (<i>NovaSatcoDX</i>)."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setOpenExternalLinks(True)
        desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        layout.addStretch()

        # Action Buttons Layout (GitHub + Report Bug + Close)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_github = QPushButton("⭐ GitHub" if not is_tr else "⭐ GitHub Deposu")
        btn_github.setToolTip("https://github.com/gokcank/SatSort")
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort")))
        btn_layout.addWidget(btn_github)

        btn_issue = QPushButton("🐛 Report Bug" if not is_tr else "🐛 Hata Bildir")
        btn_issue.setToolTip("https://github.com/gokcank/SatSort/issues/new")
        btn_issue.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/gokcank/SatSort/issues/new")))
        btn_layout.addWidget(btn_issue)

        btn_update = QPushButton("🔄 " + ("Güncellemeleri Denetle" if is_tr else "Check for Updates"))
        btn_update.clicked.connect(self._check_updates)
        btn_layout.addWidget(btn_update)

        btn_layout.addStretch()

        btn_close = QPushButton(t("T107"))  # Kapat
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _check_updates(self) -> None:
        from .update_dialog import UpdateDialog
        UpdateDialog(self).exec()
