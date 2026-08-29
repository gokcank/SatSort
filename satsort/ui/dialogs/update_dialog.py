"""
SatSort - Application Update Dialog
Displays current vs latest version, release notes, APT update command, and direct GitHub download link.
"""

from __future__ import annotations
from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QProgressBar,
    QFrame,
)

from ...core.updater import check_for_updates, UpdateInfo, APT_UPDATE_COMMAND
from ...i18n import i18n
from ... import __version__


class UpdateWorker(QThread):
    finished = Signal(object)  # Emits UpdateInfo

    def run(self) -> None:
        result = check_for_updates()
        self.finished.emit(result)


class UpdateDialog(QDialog):
    """Modern dialog displaying update status, release notes, and installation commands."""

    def __init__(self, parent=None, precomputed_result: UpdateInfo | None = None) -> None:
        super().__init__(parent)
        is_tr = i18n.current_language == "Türkçe"
        self.setWindowTitle("Güncelleme Kontrolü" if is_tr else "Check for Updates")
        self.setFixedSize(540, 420)
        self._is_tr = is_tr
        self._worker: UpdateWorker | None = None

        self._setup_ui()
        if precomputed_result:
            self._display_result(precomputed_result)
        else:
            self._start_check()

    def _setup_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 20, 24, 20)
        self.layout.setSpacing(12)

        # Header Area
        self.header_layout = QHBoxLayout()
        self.icon_lbl = QLabel("🔄")
        self.icon_lbl.setStyleSheet("font-size: 36px;")
        self.header_layout.addWidget(self.icon_lbl)

        self.title_layout = QVBoxLayout()
        self.status_title = QLabel("Güncellemeler Denetleniyor..." if self._is_tr else "Checking for Updates...")
        self.status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        self.title_layout.addWidget(self.status_title)

        self.status_sub = QLabel(f"SatSort v{__version__}")
        self.status_sub.setStyleSheet("color: #94a3b8; font-size: 13px;")
        self.title_layout.addWidget(self.status_sub)
        self.header_layout.addLayout(self.title_layout)
        self.header_layout.addStretch()
        self.layout.addLayout(self.header_layout)

        # Progress bar (visible while checking)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Content Area (dynamic)
        self.content_area = QVBoxLayout()
        self.layout.addLayout(self.content_area, stretch=1)

        # Bottom Button Bar
        self.button_layout = QHBoxLayout()
        self.btn_action = QPushButton("GitHub İndirme Sayfası" if self._is_tr else "GitHub Release Page")
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)
        self.btn_action.setVisible(False)
        self.button_layout.addWidget(self.btn_action)
        self.button_layout.addStretch()

        self.btn_close = QPushButton("Kapat" if self._is_tr else "Close")
        self.btn_close.clicked.connect(self.accept)
        self.button_layout.addWidget(self.btn_close)
        self.layout.addLayout(self.button_layout)

    def _start_check(self) -> None:
        self._worker = UpdateWorker()
        self._worker.finished.connect(self._display_result)
        self._worker.start()

    def _display_result(self, result: UpdateInfo) -> None:
        self.progress_bar.setVisible(False)

        # Clear any existing widgets in content area
        while self.content_area.count():
            item = self.content_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if result.error:
            self.icon_lbl.setText("⚠️")
            self.status_title.setText("Güncelleme Kontrolü Başarısız" if self._is_tr else "Update Check Failed")
            self.status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f87171;")
            self.status_sub.setText(
                "GitHub sunucusuyla iletişim kurulamadı." if self._is_tr else "Could not reach GitHub servers."
            )

            msg = QLabel(
                f"Lütfen internet bağlantınızı denetleyin.\n\nHata ayrıntısı: {result.error}"
                if self._is_tr
                else f"Please check your internet connection.\n\nError details: {result.error}"
            )
            msg.setWordWrap(True)
            msg.setStyleSheet("color: #cbd5e1; font-size: 13px;")
            self.content_area.addWidget(msg)
            self.content_area.addStretch()

        elif result.has_update:
            self.icon_lbl.setText("🚀")
            self.status_title.setText(
                f"Yeni Sürüm Mevcut! (v{result.latest_version})"
                if self._is_tr
                else f"New Version Available! (v{result.latest_version})"
            )
            self.status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
            self.status_sub.setText(
                f"Yüklü: v{result.current_version}  ➔  En Son: v{result.latest_version}"
                if self._is_tr
                else f"Installed: v{result.current_version}  ➔  Latest: v{result.latest_version}"
            )

            # Release Notes Box
            notes_lbl = QLabel("Sürüm Notları:" if self._is_tr else "Release Notes:")
            notes_lbl.setStyleSheet("font-weight: bold; color: #94a3b8; font-size: 12px;")
            self.content_area.addWidget(notes_lbl)

            notes_edit = QTextEdit()
            notes_edit.setReadOnly(True)
            notes_edit.setPlainText(result.release_notes if result.release_notes else "Detaylar GitHub sürüm sayfasında.")
            notes_edit.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                }
            """)
            self.content_area.addWidget(notes_edit, stretch=1)

            # APT Command Section
            apt_layout = QHBoxLayout()
            apt_input = QLineEdit(APT_UPDATE_COMMAND)
            apt_input.setReadOnly(True)
            apt_input.setStyleSheet("""
                QLineEdit {
                    font-family: monospace;
                    padding: 6px 10px;
                    border-radius: 4px;
                    border: 1px solid #334155;
                }
            """)
            apt_layout.addWidget(apt_input, stretch=1)

            btn_copy = QPushButton("Komutu Kopyala" if self._is_tr else "Copy Command")
            btn_copy.setStyleSheet("font-weight: bold; padding: 6px 12px;")

            def copy_cmd():
                clipboard = QGuiApplication.clipboard()
                if clipboard:
                    clipboard.setText(APT_UPDATE_COMMAND)
                    btn_copy.setText("Kopyalandı! ✔" if self._is_tr else "Copied! ✔")

            btn_copy.clicked.connect(copy_cmd)
            apt_layout.addWidget(btn_copy)
            self.content_area.addLayout(apt_layout)

            # GitHub link action
            self.btn_action.setVisible(True)
            self.btn_action.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(result.html_url)))

        else:
            self.icon_lbl.setText("✅")
            self.status_title.setText("SatSort Güncel!" if self._is_tr else "SatSort is Up to Date!")
            self.status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
            self.status_sub.setText(
                f"SatSort v{__version__} — En son kararlı sürümü kullanıyorsunuz."
                if self._is_tr
                else f"SatSort v{__version__} — You are using the latest stable release."
            )

            info_lbl = QLabel(
                "Yeni güncellemeler ve sürümler yayınlandığında buradan kolayca takip edebilirsiniz."
                if self._is_tr
                else "You will be notified here whenever new updates or releases are published."
            )
            info_lbl.setWordWrap(True)
            info_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; margin-top: 16px;")
            self.content_area.addWidget(info_lbl)
            self.content_area.addStretch()
